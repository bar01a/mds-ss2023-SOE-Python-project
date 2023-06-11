# syntax=docker/dockerfile:1

FROM python:3.9-slim

WORKDIR /flask-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ENV AM_I_IN_A_DOCKER_CONTAINER True

EXPOSE 5000

# copy all files in this directory to docker image in current workdir (flask-docker)
COPY . .

# run module flask
ENTRYPOINT ["python", "-m" , "flask", "run", "--host=0.0.0.0"]
