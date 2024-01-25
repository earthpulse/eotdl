# CONTRIBUTING

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

To run the tests:

```
docker-compose -f docker-compose.test.yml up

# run the API tests
docker exec eotdl-api-test pytest api/tests
```