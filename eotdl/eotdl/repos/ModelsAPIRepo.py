import requests

from ..repos import APIRepo


class ModelsAPIRepo(APIRepo):
    def __init__(self, url=None):
        super().__init__(url)

    def retrieve_models(self, name, limit):
        url = self.url + "models"
        if name is not None:
            url += "?match=" + name
        if limit is not None:
            if name is None:
                url += "?limit=" + str(limit)
            else:
                url += "&limit=" + str(limit)
        response = requests.get(url)
        return self.format_response(response)

    def create_model(self, metadata, id_token):
        response = requests.post(
            self.url + "models",
            json=metadata,
            headers={"Authorization": "Bearer " + id_token},
        )
        return self.format_response(response)

    def retrieve_model(self, name):
        response = requests.get(self.url + "models?name=" + name)
        return self.format_response(response)

    def create_version(self, model_id, id_token):
        response = requests.post(
            self.url + "models/version/" + model_id,
            headers={"Authorization": "Bearer " + id_token},
        )
        return self.format_response(response)
