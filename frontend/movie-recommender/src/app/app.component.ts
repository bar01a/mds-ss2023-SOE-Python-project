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
  filteredMovies: Movie[] = [];
  enoughLikedMovies = false;
  minLikedMoviesRequired = 2;
  searchText = '';

  ngOnInit(): void {
    this.getMovies();
  }

  getMovies(): void {
    this.movieService.getInitialMovies().subscribe(movies => {
      this.movies = movies;
      this.filteredMovies = movies;
    });
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
      this.filteredMovies = this.movies;
    } else {
      this.filteredMovies = this.movies.filter(movie =>
        movie.title.toLowerCase().includes(this.searchText.toLowerCase())
      );
    }
  }
}
