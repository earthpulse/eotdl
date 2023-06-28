from pydantic import BaseModel
from ....curation.stac import STACDataFrame
import json


class IngestSTAC:
    def __init__(self, repo, ingest_file, allowed_extensions):
        self.repo = repo
        self.ingest_file = ingest_file
        self.allowed_extensions = allowed_extensions

    class Inputs(BaseModel):
        stac_catalog: str
        dataset: str
        user: dict

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        # load the STAC catalog as a STACsetFrame
        df = STACDataFrame.from_stac_file(inputs.stac_catalog)
        # upload all assets to EOTDL
        for row in df.dropna(subset=["assets"]).iterrows():
            # for asset in df.assets.dropna().values[:10]:
            try:
                for k, v in row[1]["assets"].items():
                    data = self.ingest_file(
                        v["href"],
                        inputs.dataset,
                        allowed_extensions=self.allowed_extensions + [".tif", ".tiff"],
                    )
                    file_url = f"{self.repo.url}datasets/{data['dataset_id']}/download/{data['file_name']}"
                    df.loc[row[0], "assets"][k]["href"] = file_url
            except Exception as e:
                break
        data, error = self.repo.ingest_stac(
            json.loads(df.to_json()), inputs.dataset, inputs.user["id_token"]
        )
        if error:
            raise Exception(error)
        return self.Outputs(dataset=data)
