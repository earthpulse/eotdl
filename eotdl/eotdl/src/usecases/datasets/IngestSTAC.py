from pydantic import BaseModel
import json
from pathlib import Path

from ....curation.stac import STACDataFrame


class IngestSTAC:
    def __init__(self, repo, ingest_file, allowed_extensions):
        self.repo = repo
        self.ingest_file = ingest_file
        self.allowed_extensions = allowed_extensions

    class Inputs(BaseModel):
        stac_catalog: Path
        user: dict

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        # retrieve the user's geodb credentials
        # creds, error = self.repo.retrieve_credentials(inputs.user["id_token"])
        # self.validate_credentials(creds)
        # load the STAC catalog as a STACsetFrame
        df = STACDataFrame.from_stac_file(inputs.stac_catalog)
        catalog = df[df["type"] == "Catalog"]
        assert len(catalog) == 1, "STAC catalog must have exactly one root catalog"
        dataset_name = catalog.id.iloc[0]
        # create dataset
        data, error = self.repo.create_stac_dataset(
            dataset_name, inputs.user["id_token"]
        )
        if error:
            data, error2 = self.repo.retrieve_dataset(dataset_name)
            if error2:
                raise Exception(error)
            if data["uid"] != inputs.user["sub"]:
                raise Exception("Dataset already exists.")
            dataset_id = data["id"]
        else:
            dataset_id = data["dataset_id"]
        # TODO: check that we can ingest in geodb
        # # upload all assets to EOTDL
        # for row in df.dropna(subset=["assets"]).iterrows():
        #     # for asset in df.assets.dropna().values[:10]:
        #     try:
        #         for k, v in row[1]["assets"].items():
        #             data = self.ingest_file(
        #                 v["href"],
        #                 dataset,
        #                 allowed_extensions=self.allowed_extensions + [".tif", ".tiff"],
        #             )
        #             file_url = f"{self.repo.url}datasets/{data['dataset_id']}/download/{data['file_name']}"
        #             df.loc[row[0], "assets"][k]["href"] = file_url
        #     except Exception as e:
        #         break
        # ingest the STAC catalog into geodb
        data, error = self.repo.ingest_stac(
            json.loads(df.to_json()), dataset_id, inputs.user["id_token"]
        )
        if error:
            # TODO: delete all assets that were uploaded
            raise Exception(error)
        return self.Outputs(dataset=data)
