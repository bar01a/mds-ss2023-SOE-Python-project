export interface Movie {
  movieId: Number;
  title: string;
  genres: string[];
  image: string;
  like?: boolean | null;
}
