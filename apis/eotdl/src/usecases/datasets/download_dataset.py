from ...repos import OSRepo
from .retrieve_dataset import retrieve_dataset


def download_dataset_file(dataset_id, filename, user, version=None):
    os_repo = OSRepo()
    retrieve_dataset(dataset_id)
    # check_user_can_download_dataset(user)
    # TODO: if no version is provided, download most recent file ?
    data_stream = os_repo.data_stream
    filename = f"{filename}_{version}"
    object_info = os_repo.object_info(dataset_id, filename)
    return data_stream, object_info, filename


def download_stac_catalog():
    # TODO
    return
    # def __call__(self, inputs: Inputs) -> Outputs:
    # # check if dataset exists and user is owner
    # data = self.db_repo.retrieve("datasets", inputs.dataset_id)
    # if not data:
    #     raise DatasetDoesNotExistError()
    # dataset = STACDataset(**data)
    # if dataset.uid != inputs.user.uid:
    #     raise DatasetDoesNotExistError()
    # # retrieve from geodb
    # credentials = self.retrieve_user_credentials(inputs.user)
    # self.geodb_repo = self.geodb_repo(credentials)
    # gdf = self.geodb_repo.retrieve(inputs.dataset_id)
    # # report usage
    # self.db_repo.increase_counter("datasets", "id", dataset.id, "downloads")
    # return self.Outputs(stac=json.loads(gdf.to_json()))
