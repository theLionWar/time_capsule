# base image
FROM python:3.9-slim-buster
# setup environment variable
ENV DockerHOME=/home/app/time_capsule

# set work directory
RUN mkdir -p $DockerHOME

# where your code lives
WORKDIR $DockerHOME

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Poetry install and preparation
RUN apt-get update && apt-get -y install libpq-dev gcc
RUN pip install -U pip && pip install poetry
ENV PATH="${PATH}:/root/.poetry/bin"

# install psql client
RUN apt-get -y install postgresql-client

COPY . $DockerHOME

# install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# port where the Django app runs
EXPOSE 8000