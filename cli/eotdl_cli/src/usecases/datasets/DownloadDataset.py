from pydantic import BaseModel

class DownloadDataset():
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        dataset: str
        path: str = None
        user: dict

    class Outputs(BaseModel):
        dst_path: str

    def __call__(self, inputs: Inputs) -> Outputs:
        dst_path = self.repo.download_dataset(inputs.dataset, inputs.user['id_token'], inputs.path)
        return self.Outputs(dst_path=dst_path)