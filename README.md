# EOTDL

This repository contains de source code of the [**Earth Observation Training Data Lab** (EOTDL)](https://eotdl.vercel.app/). It contains a set of Python libraries, APIs, CLIs and User Interfaces to explore, create, manage and share datasets and Machine Learning models for Earth Observations applications.

## Library

The [eotdl library](./lib) contains the main functionality for creating datasets and models.

## APIs

### Main API

The [main API](./apis/eotdl) combines the functionality of the eotdl library with cloud storage (databases and object storage) and user management to explore, create, manage and share datasets and models.

#### Environment variables

In order to run the API, you need to set the following environment variables:

- `MONGO_URL`: the URL of the MongoDB database
- `MONGO_DB_NAME`: the name of the MongoDB database
- `AUTH0_DOMAIN`: the domain of the Auth0 tenant
- `AUTH0_CLIENT_ID`: the client ID of the Auth0 application
- `AUTH0_CLIENT_SECRET`: the client secret of the Auth0 application

#### Running tests

First, start docker

```
docer-compose up -d
```

Then, run the tests

```
docker-compose exec eotdl-api pytest --cov .
```

During development, you may want to keep test alive with

```
docker-compose exec eotdl-api ptw
```

You will need a `.env` file with the environment variables missing in the docker-compose file.
