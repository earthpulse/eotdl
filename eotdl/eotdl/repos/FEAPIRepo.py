import requests

from ..repos import APIRepo

class FEAPIRepo(APIRepo):
    def __init__(self, url=None):
        super().__init__(url)

    def retrieve_pipelines(self, name, limit):
        url = self.url + "pipelines"
        if name is not None:
            url += "?match=" + name
        if limit is not None:
            if name is None:
                url += "?limit=" + str(limit)
            else:
                url += "&limit=" + str(limit)
        response = requests.get(url)
        return self.format_response(response)
    
    def retrieve_pipeline(self, name):
        response = requests.get(self.url + "pipelines?name=" + name)
        return self.format_response(response)
    
    def get_pipeline_by_id(self, pipeline_id):
        response = requests.get(self.url + "pipelines/" + pipeline_id)
        return self.format_response(response)
    
    def create_pipeline(self, metadata, user):
        response = requests.post(
            self.url + "pipelines",
            json=metadata,
            headers=self.generate_headers(user),
        )
        return self.format_response(response)

    def complete_ingestion(self, pipeline_id, version, size, user):
        response = requests.post(
            self.url + "pipelines/complete/" + pipeline_id,
            json={"version": version, "size": size},
            headers=self.generate_headers(user),
        )
        return self.format_response(response)
    
    def deactivate_pipeline(self, pipeline_id, user):
        response = requests.patch(
            self.url + "pipelines/" + pipeline_id + "/deactivate",
            headers=self.generate_headers(user),
        )
        return self.format_response(response)
