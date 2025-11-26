const workshops = [
    {
        name: "Community Webinar 2025",
        thumbnail: "/tutorials/webinar.png",
        description: "Workshop conducted at Community Webinar on November 2025. Learn how to explore and stage datasets and models from EOTDL, train an ML model locally or in the cloud, ingest new datasets and models, create a brand new dataset and get involved in the project.",
        link: "https://github.com/earthpulse/eotdl/blob/main/tutorials/workshops/community_webinar/README.md",
    },
    {
        name: "LPS 2025",
        thumbnail: "/tutorials/lps25.png",
        description: "Workshop conducted at LPS premises on June 2025. Learn how to explore and stage datasets and models from EOTDL, train an ML model locally or in the cloud, ingest new datasets and models, create a brand new dataset and get involved in the project.",
        link: "https://github.com/earthpulse/eotdl/blob/main/tutorials/workshops/lps25/README.md",
    },
    {
        name: "PhiLab 2024",
        thumbnail: "/tutorials/philab.png",
        description: "Workshop conducted at PhiLab premises on May 2024. Learn how to explore and stage datasets and models from EOTDL, train an ML model locally or in the cloud, ingest new datasets and models, create a brand new dataset with STAC metadata and get involved in the project.",
        link: "https://github.com/earthpulse/eotdl/blob/main/tutorials/workshops/philab24/README.md",
    },
    {
        name: "BiDS 2023",
        thumbnail: "/tutorials/bids23.png",
        description: "Workshop conducted during the Big Data from Space (BiDS) 2023 conference. Lear how to explore and stage datasets and models from EOTDL, train an ML model locally or in the cloud, ingest new datasets and models, create a brand new dataset with STAC metadata and get involved in the project. A Youtube video of the workshop is available at the following link.",
        link: "https://github.com/earthpulse/eotdl/blob/main/tutorials/workshops/bids23/README.md",
    },
];

const tutorials = [
    {
        name: "Datasets & Models",
        thumbnail: "https://github.com/earthpulse/eotdl/raw/main/eotdl/eotdl.png",
        description: "Learn what EOTDL offers for training datasets and ML models for Earth Observation.",
        links: {
            "Introducing the EOTDL": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/00_eotdl.ipynb",
            "Exploring and staging Datasets and Models": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/01_exploring_and_staging.ipynb",
            "Ingesting in the EOTDL": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/02_ingesting.ipynb",
            "Training and Inference with Sentinel Hub": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/forest-map.ipynb",
        }
    },
    {
        name: "Data access",
        thumbnail: "https://upload.wikimedia.org/wikipedia/commons/7/77/A-Train_w-Time2013_Web.jpg",
        description: "Learn how to create yout own datasets from scratch.",
        links: {
            "Search Sentinel imagery": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/10_search_sentinel_imagery.ipynb",
            "Download Sentinel imagery": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/11_download_sentinel_imagery.ipynb",
        }
    },
    {
        name: "STAC",
        thumbnail: "https://stacspec.org/public/images-original/STAC-01.png",
        description: "We rely on STAC for data curation. Learn how to create STAC metadata for your datasets and models.",
        links: {
            "STAC metadata in EOTDL": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/03_stac.ipynb",
            "Datasets quality": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/04_datasets_quality.ipynb",
            // "Generate STAC metadata ": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/20_stac.ipynb",
            // "Generate STAC metadata with extensions": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/21_stac_extensions.ipynb",
            // "Introducing the STACDataFrame labeling strategy": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/22_stac_df_labeling.ipynb",
            // "Introducing the STACDataFrame items parser": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/23_stac_item_parsers.ipynb",
            // "Introducing the STACDataFrame assets generator": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/24_stac_assets_generator.ipynb",
            // "Generate STAC labels generated from SCANEO": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/25_stac_labels_scaneo.ipynb",
            // "Generate STAC labels from the filename": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/26_stac_labels_name.ipynb",
            // "Add the ML-Dataset STAC extension to a Catalog": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/27_stac_ml_dataset.ipynb",
            // "Calculate Quality metrics from your Catalog with the ML-Dataset extension": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/28_ml_dataset_quality_metrics.ipynb",
            // "Get a GeoDataFrame from STAC items": "https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/29_stac_to_geodataframe.ipynb",
        }
    },
];


export { tutorials, workshops };