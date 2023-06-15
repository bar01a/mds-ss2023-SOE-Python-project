import pandas as pd


class Movie:
    image = ""

    def __init__(self, movieId: int, title: str, genres: [str]):
        self.movieId = movieId
        self.title = title
        self.genres = genres

    def __str__(self):
        return f"MovieId: {self.movieId}, Title: {self.title}, Genres: {self.genres}"


class GenreMovieGroup:
    def __init__(self, genre: str, movies):
        self.genre = genre
        self.movies = movies


def get_top_x_percent_movies(movie_popularity_ranking: pd.DataFrame,
                             top_n_percent: float,
                             max_movies: int):
    top_x_percent_index = int(len(movie_popularity_ranking) * top_n_percent / 100)
    movies_selected = 0

    while top_x_percent_index >= 0 and movies_selected <= max_movies:
        movie_top_x = movie_popularity_ranking.iloc[top_x_percent_index]
        yield Movie(movie_top_x.movieId, movie_top_x.title, movie_top_x.genres)
        top_x_percent_index -= 1
        movies_selected += 1


def get_initial_movies_grouped(ratings, movies: pd.DataFrame, top_n_percent: float, max_movies: int):
    movie_number_of_ratings = ratings.groupby("movieId")["rating"].count()
    movie_has_n_ratings = movie_number_of_ratings.to_dict()
    unique_genres = movies["genres"].explode().unique()

    genre_movie_popularity_ranking = {}

    for genre in unique_genres:
        # get movies with genre
        fitting_movies = movies[movies.genres.apply(lambda x: genre in x)]
        # remove movies with 0 ratings
        fitting_movies["number_of_ratings"] = fitting_movies.loc[:, "movieId"].apply(
            lambda x: movie_has_n_ratings[x] if x in movie_has_n_ratings else 0)
        # sort by number of ratings
        fitting_movies.sort_values("number_of_ratings", ascending=False, inplace=True)
        fitting_movies.reset_index(drop=True, inplace=True)
        genre_movie_popularity_ranking[genre] = fitting_movies

    initial_movies_per_genre = []
    selected_movie_ids = []

    for genre in unique_genres:
        top_x_movies_enumerator = get_top_x_percent_movies(genre_movie_popularity_ranking[genre],
                                                           top_n_percent=top_n_percent,
                                                           max_movies=max_movies)
        movies_selected = []
        for top_x_movie in top_x_movies_enumerator:
            if top_x_movie.movieId not in selected_movie_ids:
                movies_selected.append(top_x_movie)
                selected_movie_ids.append(top_x_movie.movieId)
            if len(movies_selected) >= max_movies:
                break

        initial_movies_per_genre.append(GenreMovieGroup(genre, movies_selected))
    return initial_movies_per_genre
