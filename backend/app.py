from flask import Flask, request
from flask_cors import CORS, cross_origin
import os
import pandas as pd
import json
import requests
import project_secrets
import paths_to_files
import initialMovies
import association_rules_helper
import pickle
from nltk.metrics import edit_distance
from importlib import reload

reload(association_rules_helper)
reload(project_secrets)
reload(paths_to_files)
reload(initialMovies)

# if in docker, files may not be in same location
if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
    paths_to_files.path_to_movies_csv = "data/movies.csv"
    paths_to_files.path_to_links_csv = "data/links.csv"

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

ratings = pd.read_csv(paths_to_files.path_to_ratings_csv)
movies = pd.read_csv(paths_to_files.path_to_movies_csv)
links = pd.read_csv(paths_to_files.path_to_links_csv)
movies = pd.merge(movies, links, on="movieId", how="left")
movies["image"] = None

with (open("models/association_results_support_0003_confidence_37.pkl", "rb")) as openfile:
    association_results = pickle.load(openfile)

recommendationDict = association_rules_helper.create_movies_recommendation_dict(association_results)
extended_recommendation_dict = association_rules_helper.extend_recommendation_dict_both_ways(recommendationDict, 7)

movies["genres"] = movies["genres"].apply(lambda x: x.split("|"))
poster_path = "https://image.tmdb.org/t/p/w400"
movie_detail_path = "https://api.themoviedb.org/3/movie/"
tmdb_headers = {
    "accept": "application/json",
    "Authorization": "Bearer " + project_secrets.api_key
}


def get_image_path(movie_id):
    movie_short = movies.loc[movies["movieId"] == movie_id, ["image", "tmdbId"]].iloc[0]
    if movie_short["image"] is not None:
        print("Cached image:", movie_short["image"])
        return movie_short["image"]
    response = requests.get(movie_detail_path + str(movie_short["tmdbId"]), headers=tmdb_headers)
    if response.status_code != 200:
        movies.loc[movies["movieId"] == movie_id, "image"] = ""
        return ""
    path_to_image = poster_path + response.json()["poster_path"]
    movies.loc[movies["movieId"] == movie_id, "image"] = path_to_image
    print("Image", movie_id, path_to_image)
    return path_to_image


def get_initial_movies_grouped():
    result = initialMovies.get_initial_movies_grouped(ratings, movies, 1, 3)  # movies[0:6]
    for group in result:
        group.movies = pd.DataFrame([movies[movies.movieId == movie.movieId].iloc[0] for movie in group.movies]).reset_index()
        group.movies.loc[:, "image"] = group.movies["movieId"].apply(get_image_path)
    return result


initial_movies_grouped = get_initial_movies_grouped()


@app.route('/')
def index():
    return 'Server Works juhu!<br><a href="/api/initial-movies">Access initial movies</a>'


@app.route('/api/initial-movies', methods=['GET'])
@cross_origin()
def get_initial_movies():
    genres = {}

    for genre in movies["genres"].explode().unique():
        genres[genre] = []

    serializable_initial_movies_grouped = []

    for initial_movies_group in initial_movies_grouped:
        group = {"genre": initial_movies_group.genre,
                 "movies": initial_movies_group.movies.to_dict('records')}
        serializable_initial_movies_grouped.append(group)

    return json.dumps(serializable_initial_movies_grouped)


@app.route('/api/get-matching-movies', methods=['GET'])
@cross_origin()
def get_matching_movies():
    matches = movies.loc[association_rules_helper.contains_movie_title(movies["title"], request.args.get('query')), :]
    matches["distance"] = matches.loc[:, "title"].apply(lambda title: edit_distance(title, request.args.get('query')))
    matches = matches.sort_values(by="distance", ascending=True)
    matches.loc[matches[0:7].index, "image"] = [get_image_path(movieId) for movieId in matches.iloc[0:7]["movieId"]]
    print(matches[0:7])
    return json.dumps(matches.to_dict('records'))


@app.route('/api/get-recommendations', methods=['POST'])
@cross_origin()
def get_recommendations():
    rated_movies = request.json
    recommendation_groups = association_rules_helper.get_recommendations(rated_movies, movies, extended_recommendation_dict, 3)
    for recGroup in recommendation_groups:
        for rec in recGroup["recommendations"]:
            rec["image"] = get_image_path(rec["movieId"])
    return json.dumps(recommendation_groups)

