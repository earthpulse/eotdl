# CONTRIBUTING

## Events

To add an event to the website, you have to edit the [`ui/src/routes/events.json`](ui/src/routes/events.json) file.

The event have to be a JSON object with the following properties:

- **title**: the title of the event
- **description**: the description of the event
- **date**: the date of the event
- **link**: the link to the event

Once the file is edited, you create a PR to the `develop` branch so we can review it and merge it.

## Datasets

If you would like us to include a new dataset, create an issue with the following information and we'll add it to the list.

- **Name**: dataset name
- **Size**: dataset size in Gigaytes
- **Source**: data source (i.e Sentinel 1, Sentinel 2, Drone, ...)
- **Technique**: AI technique that can be solved with the dataset (i.e classification, object detection, ...)
- **Application**: the application enabled by the dataset (i.e land cover, urban development, ...)
- **AOI**: geographical extension of the dataset
- **Time Span**: temporal extension of the dataset
- **License**: the license of the dataset
- **Download link**: the link to download the dataset
- **References**: links to references (i.e papers, blog posts, repos, ...)

And any other relevant information.

## Code

If you want to contribute to the codebase of EOTDL, first fork this repository and clone your fork to your machine.

Then, create a new branch and implement your work, which should include testing if necessary.

Finally, create a Pull Request to the `develop` branch so we can review it and merge it.

To run the api:

```
docker-compose up
```

The first time you run it you have to initialize the database calling the `/admin/init-db` endpoint using the admin api key provided in the docker-compose file. This will create the `tiers` and `tags` collections required for the API to work.

```
curl localhost:8010/admin/init-db -H 'X-API-Key: 12345678' # or the url/api key of the api
```

To run the cli:

```
export EOTDL_API_URL=http://localhost:8010 # or the url of the api
python eotdl/main.py --help # or any other command
```

To run the tests:

```
docker-compose -f docker-compose.test.yml up

# run the API tests
docker exec eotdl-api-test pytest api/tests
```