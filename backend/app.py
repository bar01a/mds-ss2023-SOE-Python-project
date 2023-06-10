from flask import Flask
from flask_cors import CORS, cross_origin
import pandas as pd
import json
import requests
import secrets
from importlib import reload
reload(secrets)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

movies = pd.read_csv("path/to/movies.csv")
links = pd.read_csv("path/to/links.csv")
movies["genres"] = movies["genres"].apply(lambda x: x.split("|"))
poster_path = "https://image.tmdb.org/t/p/w400"
movie_detail_path = "https://api.themoviedb.org/3/movie/"
tmdb_headers = {
    "accept": "application/json",
    "Authorization": "Bearer " + secrets.api_key
}

def get_image_path(x):
    response = requests.get(movie_detail_path + str(x), headers=tmdb_headers)
    return poster_path + response.json()["poster_path"]

initial_movies = movies[0:6]
initial_movies = pd.merge(initial_movies, links, on = "movieId", how = "left")
initial_movies["image"] = initial_movies["tmdbId"].apply(get_image_path)

@app.route('/')
def index():
    return 'Server Works juhu!'

@app.route('/api/initial-movies', methods = ['GET'])
@cross_origin()
def get_initial_movies():
    return json.dumps(initial_movies.to_dict('records'))
