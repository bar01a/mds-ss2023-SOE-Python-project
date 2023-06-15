export interface Movie {
  movieId: Number;
  title: string;
  genres: string[];
  image: string;
  like?: boolean | null;
}

export interface GenreMovieGroup {
  genre: string;
  movies: Movie[];
}

export interface MovieRecommendations {
  movie: Movie;
  recommendations: Movie[];
}