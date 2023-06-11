from flask import Flask
from flask_cors import CORS, cross_origin
import os
import pandas as pd
import json
import requests
import project_secrets
import paths_to_files
from importlib import reload
reload(project_secrets)
reload(paths_to_files)

# if in docker, files may not be in same location
if os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
    paths_to_files.path_to_movies_csv = "data/movies.csv"
    paths_to_files.path_to_links_csv = "data/links.csv"


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

movies = pd.read_csv(paths_to_files.path_to_movies_csv)
links = pd.read_csv(paths_to_files.path_to_links_csv)
movies["genres"] = movies["genres"].apply(lambda x: x.split("|"))
poster_path = "https://image.tmdb.org/t/p/w400"
movie_detail_path = "https://api.themoviedb.org/3/movie/"
tmdb_headers = {
    "accept": "application/json",
    "Authorization": "Bearer " + project_secrets.api_key
}

def get_image_path(x):
    response = requests.get(movie_detail_path + str(x), headers=tmdb_headers)
    return poster_path + response.json()["poster_path"]


initial_movies = movies[0:6]
initial_movies = pd.merge(initial_movies, links, on="movieId", how="left")
initial_movies["image"] = initial_movies["tmdbId"].apply(get_image_path)

@app.route('/')
def index():
    return 'Server Works juhu!<br><a href="/api/initial-movies">Access initial movies</a>'

@app.route('/api/initial-movies', methods=['GET'])
@cross_origin()
def get_initial_movies():
    genres = {}

    for genre in movies["genres"].explode().unique():
        genres[genre] = []

    for movie in initial_movies.to_dict('records'):
        movie_genres = movie["genres"]
        for genre in movie_genres:
            if genre in genres:
                genres[genre].append(movie)
    
    sorted_movies = [{"genre": genre, "movies": movie_list} for genre, movie_list in genres.items()]

    return json.dumps(sorted_movies)
