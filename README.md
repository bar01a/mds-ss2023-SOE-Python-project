# Movie Recommendation Project
This project was performed by Bauer, Gisser & Resavac on behalf of the course SOE/Python.

## Project Description
The task was to develop an application that suggets movies to the user based on their ratings of movies they have already seen.

The following data basis was used for this:
* [grouplens](https://grouplens.org/datasets/movielens/25m/)
* [movielens](https://movielens.org/)

## Instructions to run the application
In order to successfully launch the developed application, the following steps must be carried out for the frontend and backend:

### Frontend
Open a terminal, navigate into the "movie-recommender" folder and run `ng serve` for a dev server. Then, open `http://localhost:4200/` in a browser. (The application will automatically reload if you change any of the source files.)

*For more information on this please refer to the README in the frontend directory.*

### Backend
* Change the API_KEY in `backend/project_secrets.py`.
* Either paste the "ratings.csv" file into `backend/data` **(recommended)** or adjust the path to your "ratings.csv" file in `backend/paths_to_files.py`. You can download the data from here: [MovieLens 25M Dataset](https://grouplens.org/datasets/movielens/25m/) (same link as in project description section).

**Manually**<br>
Open anaconda prompt (or in which environment flask was installed), navigate into "backend" folder and run `flask run`.</br>

**Using Docker**<br>
Navigate into "backend" folder (project root might also work) and run `docker compose up --build` while docker is running.</br>

## Further material of this project
We have documented our first thoughts / steps in Deepnote notebooks. These can be viewed under the following link: [Deepnote](https://deepnote.com/workspace/fh-dqda-03406136-d2b4-4578-a026-1c3266c20c2e/project/SOEPython-b58ee753-d2eb-4fbf-a7b3-c86711836b6c/notebook/EDA-56e3bf05300541a182576fe8f80cd19b)
