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

    def retrieve_model(self, name):
        response = requests.get(self.url + "models?name=" + name)
        return self.format_response(response)
    
    def create_model(self, metadata, user):
        response = requests.post(
            self.url + "models",
            json=metadata,
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def complete_ingestion(self, model_id, version, size, user):
        response = requests.post(
            self.url + "models/complete/" + model_id,
            json={"version": version, "size": size},
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def deactivate_model(self, model_name, user):
        response = requests.patch(
            self.url + "models/deactivate/" + model_name,
            headers=self.generate_headers(user),
        )
        return self.format_response(response)
