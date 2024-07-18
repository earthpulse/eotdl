const workshops = [
    {
        name: "PhiLab 2024",
        thumbnail: "",
        description:"Lorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium debitis voluptates corporis enim mollitia voluptatum officia impedit minus sit, modi, nesciunt perspiciatis fuga eum molestias eaque similique alias, quos vel.",
        link: "https://github.com/earthpulse/eotdl/blob/main/tutorials/workshops/philab24/README.md",
    },
    {
        name: "BiDS 2023",
        thumbnail: "",
        description:"Lorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium debitis voluptates corporis enim mollitia voluptatum officia impedit minus sit, modi, nesciunt perspiciatis fuga eum molestias eaque similique alias, quos vel.",
        link: "https://github.com/earthpulse/eotdl/blob/main/tutorials/workshops/bids23/README.md",
    },
];

const tutorials = [
        {
        name: "Datasets",
        thumbnail: "",
        description:"Lorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium debitis voluptates corporis enim mollitia voluptatum officia impedit minus sit, modi, nesciunt perspiciatis fuga eum molestias eaque similique alias, quos vel.",
        links: {"Introducing the EOTDL":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/00_eotdl.ipynb",
            "Exploring the EOTDL":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/01_exploring.ipynb",
            "Ingesting in the EOTDL":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/02_ingesting.ipynb",
            "Creating and ingesting Q1 datasets":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/03_q1_datasets.ipynb",
            "Creating and ingesting Q2 datasets":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/04_q2_datasets.ipynb",
            "Training and Inference with Sentinel Hub":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/forest-map.ipynb",
        	}
		},
        {
        name: "Data access",
        thumbnail: "",
        description:"Lorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium debitis voluptates corporis enim mollitia voluptatum officia impedit minus sit, modi, nesciunt perspiciatis fuga eum molestias eaque similique alias, quos vel.",
        links: {"Search Sentinel imagery":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/10_search_sentinel_imagery.ipynb",
            "Download Sentinel imagery":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/11_download_sentinel_imagery.ipynb",
        	}
		},
        {
        name: "STAC",
        thumbnail: "",
        description:"Lorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium debitis voluptates corporis enim mollitia voluptatum officia impedit minus sit, modi, nesciunt perspiciatis fuga eum molestias eaque similique alias, quos vel.",
        links: {"Generate STAC metadata ":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/20_stac.ipynb",
            "Generate STAC metadata with extensions":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/21_stac_extensions.ipynb",
            "Introducing the STACDataFrame labeling strategy":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/22_stac_df_labeling.ipynb",
            "Introducing the STACDataFrame items parser":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/23_stac_item_parsers.ipynb",
            "Introducing the STACDataFrame assets generator":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/24_stac_assets_generator.ipynb",
            "Generate STAC labels generated from SCANEO":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/25_stac_labels_scaneo.ipynb",
            "Generate STAC labels from the filename":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/26_stac_labels_name.ipynb",
            "Add the ML-Dataset STAC extension to a Catalog":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/27_stac_ml_dataset.ipynb",
            "Calculate Quality metrics from your Catalog with the ML-Dataset extension":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/28_ml_dataset_quality_metrics.ipynb",
            "Get a GeoDataFrame from STAC items":"https://github.com/earthpulse/eotdl/blob/main/tutorials/notebooks/29_stac_to_geodataframe.ipynb",
        	}
		},
	];


export {tutorials, workshops};