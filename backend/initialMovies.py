import pandas as pd


class Movie:
    poster_path = ""

    def __init__(self, movie_id: int, title: str, genres: [str]):
        self.movie_id = movie_id
        self.title = title
        self.genres = genres

    def __str__(self):
        return f"MovieId: {self.movie_id}, Title: {self.title}, Genres: {self.genres}"


class GenreMovieGroup:
    def __init__(self, genre: str, movies: [Movie]):
        self.genre = genre
        self.movies = movies


def get_rel_movie_position_in_genre_group(movie_id, genre):
    df = genre_movie_popularity_ranking[genre]
    requested_movie = df[df.movieId == movie_id]
    return requested_movie.index[0] / len(df) if len(requested_movie) > 0 else None


def get_top_x_percent_movies(movie_popularity_ranking: pd.DataFrame,
                             genre: str,
                             top_n_percent: float,
                             max_movies: int,
                             must_be_highest_in_genre=False):
    top_x_percent_index = int(len(movie_popularity_ranking) * top_n_percent / 100)
    group = GenreMovieGroup(genre, [])

    while top_x_percent_index >= 0 and len(group.movies) < max_movies:
        movie_top_x = movie_popularity_ranking.iloc[top_x_percent_index]
        highest_compared_to_other_genres = True
        for movie_genre in movie_top_x.genres:
            # check if the movie has a higher ranking (lower relative index) in a different genre
            if movie_genre != genre and \
                    get_rel_movie_position_in_genre_group(movie_top_x.movieId,
                                                          movie_genre) <= top_x_percent_index / len(
                movie_popularity_ranking):
                highest_compared_to_other_genres = False
                break
        if highest_compared_to_other_genres or not must_be_highest_in_genre:
            group.movies.append(Movie(movie_top_x.movieId, movie_top_x.title, movie_top_x.genres))
        top_x_percent_index -= 1

    return group


def get_initial_movies(ratings, movies: pd.DataFrame, max_movies: int):
    movie_number_of_ratings = ratings.groupby("movieId")["rating"].count()
    movie_has_n_ratings = movie_number_of_ratings.to_dict()
    movies["genres"] = movies["genres"].apply(lambda x: x.split("|"))
    unique_genres = movies["genres"].explode().unique()

    genre_movie_popularity_ranking = {}

    for genre in unique_genres:
        fitting_movies = movies[movies.genres.apply(lambda x: genre in x)]
        fitting_movies["number_of_ratings"] = fitting_movies["movieId"].apply(
            lambda x: movie_has_n_ratings[x] if x in movie_has_n_ratings else 0)
        fitting_movies.sort_values("number_of_ratings", ascending=False, inplace=True)
        fitting_movies.reset_index(drop=True, inplace=True)
        genre_movie_popularity_ranking[genre] = fitting_movies

    initial_movies_per_genre = []
    for genre in unique_genres:
        movies_for_genre = get_top_x_percent_movies(genre_movie_popularity_ranking[genre], genre,
                                                    top_n_percent=5, max_movies=max_movies)
        initial_movies_per_genre.append(movies_for_genre)
    return initial_movies_per_genre
