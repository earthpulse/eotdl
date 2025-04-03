import requests

from ..repos import APIRepo

class DatasetsAPIRepo(APIRepo):
    def __init__(self, url=None):
        super().__init__(url)

    def retrieve_datasets(self, name, limit):
        url = self.url + "datasets"
        if name is not None:
            url += "?match=" + name
        if limit is not None:
            if name is None:
                url += "?limit=" + str(limit)
            else:
                url += "&limit=" + str(limit)
        response = requests.get(url)
        return self.format_response(response)
    
    def retrieve_dataset(self, name):
        response = requests.get(self.url + "datasets?name=" + name)
        return self.format_response(response)
    
    def get_dataset_by_id(self, dataset_id):
        response = requests.get(self.url + "datasets/" + dataset_id)
        return self.format_response(response)
    
    def create_dataset(self, metadata, user):
        response = requests.post(
            self.url + "datasets",
            json=metadata,
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def complete_ingestion(self, dataset_id, version, size, user):
        response = requests.post(
            self.url + "datasets/complete/" + dataset_id,
            json={"version": version, "size": size},
            headers=self.generate_headers(user),
        )
        return self.format_response(response)
