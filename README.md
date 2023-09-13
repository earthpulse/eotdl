# EOTDL

This repository contains de source code of the [**Earth Observation Training Data Lab** (EOTDL)](https://eotdl.vercel.app/). It contains a set of Python libraries, APIs, CLIs and User Interfaces to explore, create, manage and share datasets and Machine Learning models for Earth Observations applications.

## Library and CLI

The [eotdl library](./eotdl) contains the main functionality for creating datasets and models, as well as the CLI.

## APIs

### Main API

The [main API](./apis/eotdl) combines the functionality of the eotdl library with cloud storage (databases and object storage) and user management to explore, create, manage and share datasets and models.

#### Environment variables

In order to run the API, you need to set the following environment variables:

- `MONGO_URL`: the URL of the MongoDB database
- `MONGO_DB_NAME`: the name of the MongoDB database
- `S3_ENDPOINT`: the endpoint of the S3 object storage
- `ACCESS_KEY_ID`: the access key ID of the S3 object storage
- `SECRET_ACCESS_KEY`: the secret access key of the S3 object storage
- `S3_BUCKET`: the name of the S3 bucket to store the datasets
- `S3_SSL`: whether to use SSL to connect to the S3 object storage (optinal, True by default)
- `S3_REGION`: the region of the S3 object storage
- `AUTH0_DOMAIN`: the domain of the Auth0 tenant
- `AUTH0_CLIENT_ID`: the client ID of the Auth0 application
- `AUTH0_CLIENT_SECRET`: the client secret of the Auth0 application
- `ADMIN_API_KEY`: the API key to access the admin endpoints
- `TZ`: Your time zone (for example, `Europe/Madrid`. Optional, `UTC` by default)
- `API_BASE_URL`: the base url used to build the download links (in our case, https://eotdl.com)
- `EOX_PROVISIONINGS_URL`: ...
- `EOX_VAULT_URL`: ...
- `EOX_VAULT_ROLE_ID`: ...
- `EOX_VAULT_SECRET_ID`: ...

CLI environment variables:

- `EOTDL_API_URL`: the URL of the API to run the CLI against (by default, https://api.eotdl.com)
- `EOTDL_DOWNLOAD_PATH`: the path to download the datasets (by default, `~/.cache/eotdl`)

#### Running tests

First, start docker

```
docker-compose -f docker-compose.test.yml up -d
```

Then, run the tests

```
docker exec eotdl-api-test pytest api --cov api --cov-report term-missing
docker exec eotdl-test poetry run pytest --cov eotdl --cov-report term-missing
```

During development, you may want to keep test alive with

```
docker exec eotdl-api-test ptw api
docker exec eotdl-test poetry run ptw
```

You will need a `.env` file with the environment variables missing in the docker-compose file.

E2E UI generate tests

```
cd uis/eotdl
yarn dev

# first time to login and save cookies
yarn playwright codegen http://localhost:5173 --save-storage=auth.json

# next times to run tests
yarn playwright codegen http://localhost:5173 --load-storage=auth.json
```

#### Running the API

```
docker-compose up -d
```
