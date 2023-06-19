# mds-ss2023-SOE-Python-project
Git repo for Solution Engineering with Python project

## Frontend
Open terminal, navigate into "movie-recommender" folder and run `ng serve` for a dev server. 
Then, open `http://localhost:4200/` in browser. The application will automatically reload if you change any of the source files.

For more information refer to the README in the frontend directory. 

## Backend
* Change API_KEY in `backend/project_secrets.py`
* Change file paths in `backend/paths_to_files.py`

### Manually:
Open anaconda prompt (or in which environment flask was installed), navigate into "backend" folder and run `flask run`.

### Using Docker:
Navigate into "backend" folder and run `docker compose up --build`.
