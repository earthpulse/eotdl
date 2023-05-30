from pydantic import BaseModel


class UpdateDataset:
    def __init__(self, repo, logger):
        self.repo = repo
        self.logger = logger

    class Inputs(BaseModel):
        name: str
        path: str = None
        user: dict

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        # allow only zip files
        if not inputs.path.endswith(".zip"):
            raise Exception("Only zip files are allowed")
        self.logger("Updating dataset...")
        data, error = self.repo.update_dataset(
            inputs.name, inputs.path, inputs.user["id_token"]
        )
        if error:
            raise Exception(error)
        self.logger("Done")
        return self.Outputs(dataset=data)
