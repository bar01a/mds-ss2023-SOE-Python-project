import { Component } from '@angular/core';
import { GenreMovieGroup, Movie, MovieRecommendations } from "./Movie";
import { MoviesService } from "./movies.service";
import { Observable, Subject, debounceTime, distinctUntilChanged, switchMap } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.less']
})
export class AppComponent {
  title = 'movie-recommender';

  constructor(private movieService: MoviesService) { }

  ratedMovies: Movie[] = [];
  moviesGroups: GenreMovieGroup[] = [];
  enoughLikedMovies = false;
  minLikedMoviesRequired = 2;
  searchText = '';
  searchResults: Movie[] = [];
  movieRecommendations: MovieRecommendations[] = [];
  searchSubject = new Subject<string>();

  ngOnInit(): void {
    this.getMovies();
    this.searchSubject
    .pipe(
      debounceTime(700),
      distinctUntilChanged(),
      switchMap((searchQuery) => this.movieService.getMatchingMovies(searchQuery))
    )
    .subscribe((results) => (this.searchResults = results));
  }

  getMovies(): void {
    this.movieService.getInitialMovies().subscribe(movies => {
      this.moviesGroups = movies;
    });
  }

  isMovieRated(movie: Movie, liked: boolean) {
    return this.ratedMovies.find(ratedMovie => ratedMovie.movieId === movie.movieId && ratedMovie.like === liked) !== undefined;
  }

  likeMovie(movie: Movie) {
    let ratedMovie = this.ratedMovies.find(movie2 => movie2.movieId == movie.movieId);

    // movie not yet rated
    if (ratedMovie === undefined) {
      this.ratedMovies.push({
        movieId: movie.movieId,
        title: movie.title,
        genres: movie.genres,
        image: movie.image,
        like: true
      });
    } else if (ratedMovie.like === true) {
      // If already liked, remove from rated movies
      this.ratedMovies = this.ratedMovies.filter(movie => movie.movieId !== ratedMovie?.movieId);
    } else {
      // otherwise change to like
      ratedMovie.like = true;
    }

    this.enoughLikedMovies = this.ratedMovies.filter(movie => movie.like).length >= this.minLikedMoviesRequired;
  }

  dislikeMovie(movie: Movie) {
    let ratedMovie = this.ratedMovies.find(movie2 => movie2.movieId == movie.movieId);

    // movie not yet rated
    if (ratedMovie === undefined) {
      this.ratedMovies.push({
        movieId: movie.movieId,
        title: movie.title,
        genres: movie.genres,
        image: movie.image,
        like: false
      });
    } else if (ratedMovie.like === false) {
      // If already disliked, remove from rated movies
      this.ratedMovies = this.ratedMovies.filter(movie => movie.movieId !== ratedMovie?.movieId);
    } else {
      // otherwise change to dislike
      ratedMovie.like = false;
    }

    this.enoughLikedMovies = this.ratedMovies.filter(movie => movie.like).length >= this.minLikedMoviesRequired;
  }

  getRecommendations(): void {
    this.movieService.getRecommendations(this.ratedMovies).subscribe(movieRecommendations => this.movieRecommendations = movieRecommendations);
  }

  searchMovies(): void {
    if (this.searchText.trim() === '') {
      this.searchResults = [];
      return;
    }

    this.searchSubject.next(this.searchText.trim());
  }

  goBack(): void {
    this.movieRecommendations = []; // Clear the recommendations
  }
}
