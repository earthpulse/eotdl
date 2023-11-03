from ...repos import OSRepo
from .retrieve_model import retrieve_model


def download_model_file(model_id, filename, user, version=None):
    os_repo = OSRepo()
    retrieve_model(model_id)
    # check_user_can_download_model(user)
    # TODO: if no version is provided, download most recent file ?
    data_stream = os_repo.data_stream
    filename = f"{filename}_{version}"
    object_info = os_repo.object_info(model_id, filename)
    return data_stream, object_info, filename


def download_stac_catalog():
    # TODO
    return
    # def __call__(self, inputs: Inputs) -> Outputs:
    # # check if model exists and user is owner
    # data = self.db_repo.retrieve("models", inputs.model_id)
    # if not data:
    #     raise modelDoesNotExistError()
    # model = STACmodel(**data)
    # if model.uid != inputs.user.uid:
    #     raise modelDoesNotExistError()
    # # retrieve from geodb
    # credentials = self.retrieve_user_credentials(inputs.user)
    # self.geodb_repo = self.geodb_repo(credentials)
    # gdf = self.geodb_repo.retrieve(inputs.model_id)
    # # report usage
    # self.db_repo.increase_counter("models", "id", model.id, "downloads")
    # return self.Outputs(stac=json.loads(gdf.to_json()))
