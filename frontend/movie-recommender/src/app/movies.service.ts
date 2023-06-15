import { Injectable } from '@angular/core';
import {GenreMovieGroup, Movie, MovieRecommendations} from "./Movie";
import {catchError, Observable, of, tap} from "rxjs";
import {HttpClient, HttpHeaders, HttpParams} from "@angular/common/http";

@Injectable({
  providedIn: 'root'
})
export class MoviesService {

  constructor(private http: HttpClient) { }

  private api_url = "http://127.0.0.1:5000"
  private movies_get_url = "/api/initial-movies";  // URL to web api
  private movies_get_recommendation_url = "/api/get-recommendations"
  private movies_get_matching_movies_url = "/api/get-matching-movies"

  getInitialMovies(): Observable<GenreMovieGroup[]> {
    // MOCK data
    /*
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
    */

    return this.http.get<GenreMovieGroup[]>(this.api_url + this.movies_get_url)
      .pipe(
        tap(data => {console.log(data);})
      );
  }

  getMatchingMovies(query: string): Observable<Movie[]> {
    let params = new HttpParams().set("query", query);

    return this.http.get<Movie[]>(this.api_url + this.movies_get_matching_movies_url, {params: params}).pipe(
      tap(data => console.log(data)),
      catchError(err => {console.error(err); return [];})
    );
  }

  getRecommendations(ratedMovies: Movie[]): Observable<MovieRecommendations[]> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type':  'application/json'
      })
    };

    return this.http.post<MovieRecommendations[]>(this.api_url + this.movies_get_recommendation_url, ratedMovies, httpOptions).pipe(
      tap(data => console.log(data)),
      catchError(err => {console.error(err); return [];})
    );
  }
}
