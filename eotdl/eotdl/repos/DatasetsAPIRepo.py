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
    
    def retrieve_private_datasets(self, user):
        url = self.url + "datasets/private"
        response = requests.get(url, headers=self.generate_headers(user))
        return self.format_response(response)
    
    def retrieve_dataset(self, name):
        response = requests.get(self.url + "datasets?name=" + name)
        return self.format_response(response)
    
    def retrieve_private_dataset(self, name, user):
        response = requests.get(self.url + "datasets/private?name=" + name, headers=self.generate_headers(user))
        return self.format_response(response)
    
    def get_dataset_by_id(self, dataset_id):
        response = requests.get(self.url + "datasets/" + dataset_id)
        return self.format_response(response)
    
    def create_dataset(self, metadata, user, private=False):
        if private:
            metadata["visibility"] = "private"
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
    
    def deactivate_dataset(self, dataset_name, user):
        response = requests.patch(
            self.url + "datasets/deactivate/" + dataset_name,
            headers=self.generate_headers(user),
        )
        return self.format_response(response)
