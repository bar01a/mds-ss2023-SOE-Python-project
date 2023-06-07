import { Injectable } from '@angular/core';
import {Movie} from "./Movie";
import {catchError, Observable, of, tap} from "rxjs";
import {HttpClient} from "@angular/common/http";

@Injectable({
  providedIn: 'root'
})
export class MoviesService {

  constructor(private http: HttpClient) { }

  private api_url = "http://127.0.0.1:5000"
  private movies_get_url = "/api/initial-movies";  // URL to web api

  getInitialMovies(): Observable<Movie[]> {
    // MOCK data
    return of([
      {
        movieId: 1,
        title: "John Wick 4",
        genres: ["Action", "Drama"],
        image: "https://www.themoviedb.org/t/p/original/uPQUZETVGwqAjbhwhSFZZqkEdCp.jpg"
      },
      {
        movieId: 2,
        title: "Fast & Furious 10",
        genres: ["Action", "Comedy"],
        image: "https://www.themoviedb.org/t/p/w440_and_h660_face/j3S6HI4omonneHjZN9xypYVfEt0.jpg"
      }
    ]);

    return this.http.get<Movie[]>(this.api_url + this.movies_get_url)
      .pipe(
        tap(data => {console.log(data);})
      );
  }
}
