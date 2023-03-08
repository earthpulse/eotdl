# eotdl 

This is the main library for EOTDL.

## Environment variables

In order to run the library, you need to set the following environment variables:

- `MONGO_URL`: the URL of the MongoDB database
- `MONGO_DB_NAME`: the name of the MongoDB database
- `AUTH0_DOMAIN`: the domain of the Auth0 tenant
- `AUTH0_CLIENT_ID`: the client ID of the Auth0 application
- `AUTH0_CLIENT_SECRET`: the client secret of the Auth0 application


## Running tests

First, start docker

```
docer-compose up -d
```

Then, run the tests

```
docker-compose exec eotdl-lib-test pytest src/tests --cov src
```

During development, you may want to keep test alive with

```
docker-compose exec eotdl-lib-test ptw src/tests 
```

You will need a `.env` file with the missing environment variables.