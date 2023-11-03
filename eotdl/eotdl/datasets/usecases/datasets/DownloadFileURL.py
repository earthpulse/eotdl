from pydantic import BaseModel


class DownloadFileURL:
    def __init__(self, repo, logger, progress=True):
        self.repo = repo
        self.logger = logger if logger else print
        self.progress = progress

    class Inputs(BaseModel):
        url: str
        path: str = None
        user: dict

    class Outputs(BaseModel):
        dst_path: str

    def __call__(self, inputs: Inputs) -> Outputs:
        dst_path = self.repo.download_file_url(
            inputs.url, inputs.path, inputs.user["id_token"], progress=self.progress
        )
        return self.Outputs(dst_path=dst_path)
