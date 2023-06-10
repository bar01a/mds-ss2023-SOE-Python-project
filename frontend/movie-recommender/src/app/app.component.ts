import { Component } from '@angular/core';
import { Movie } from "./Movie";
import { MoviesService } from "./movies.service";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.less']
})
export class AppComponent {
  title = 'movie-recommender';

  constructor(private movieService: MoviesService) { }

  movies: Movie[] = [];
  filteredMovies: { genre: string, movies: Movie[] }[] = [];
  enoughLikedMovies = false;
  minLikedMoviesRequired = 2;
  searchText = '';

  ngOnInit(): void {
    this.getMovies();
  }

  getMovies(): void {
    this.movieService.getInitialMovies().subscribe(movies => {
      this.movies = movies;
      this.filteredMovies = this.groupMoviesByGenre(movies);
    });
  }

  groupMoviesByGenre(movies: Movie[]): { genre: string, movies: Movie[] }[] {
    const groupedMovies: { [key: string]: Movie[] } = {};

    for (const movie of movies) {
      for (const genre of movie.genres) {
        if (groupedMovies.hasOwnProperty(genre)) {
          groupedMovies[genre].push(movie);
        } else {
          groupedMovies[genre] = [movie];
        }
      }
    }

    return Object.entries(groupedMovies).map(([genre, movies]) => ({ genre, movies }));
  }

  likeMovie(movie: Movie) {
    // If already liked, set to null
    movie.like = movie.like === true ? null : true;
    this.enoughLikedMovies = this.movies.filter(movie => movie.like).length >= this.minLikedMoviesRequired;
  }

  dislikeMovie(movie: Movie) {
    // If already disliked, set to null
    movie.like = movie.like === false ? null : false;
    this.enoughLikedMovies = this.movies.filter(movie => movie.like).length >= this.minLikedMoviesRequired;
  }

  searchMovies(): void {
    if (this.searchText.trim() === '') {
      this.filteredMovies = this.groupMoviesByGenre(this.movies);
    } else {
      const filteredMovies: { genre: string, movies: Movie[] }[] = [];

      for (const group of this.filteredMovies) {
        const filteredGroupMovies = group.movies.filter(movie =>
          movie.title.toLowerCase().includes(this.searchText.toLowerCase())
        );

        if (filteredGroupMovies.length > 0) {
          filteredMovies.push({
            genre: group.genre,
            movies: filteredGroupMovies
          });
        }
      }

      this.filteredMovies = filteredMovies;
    }
  }
}