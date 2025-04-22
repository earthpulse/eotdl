import requests

from ..repos import APIRepo


class STACAPIRepo(APIRepo):
    def __init__(self, url=None):
        super().__init__(url)

    def status(self):
        response = requests.get(self.url + "stac")
        return self.format_response(response)
    
    def collections(self):
        response = requests.get(self.url + "stac/collections")
        return self.format_response(response)

    def collection(self, collection_name):
        response = requests.get(self.url + f"stac/collections/{collection_name}")
        return self.format_response(response)

    def items(self, collection_id):
        response = requests.get(self.url + f"stac/collections/{collection_id}/items")
        return self.format_response(response)

    def item(self, collection_id, item_id):
        response = requests.get(self.url + f"stac/collections/{collection_id}/items/{item_id}")
        return self.format_response(response)
    
    def search(self, collection_id, query):
        body = {"collection_id": collection_id}
        if query is not None:
            body["query"] = query
        response = requests.post(self.url + f"stac/search", json=body)
        return self.format_response(response)
    
    def search_columns(self, collection_id):
        response = requests.get(self.url + f"stac/search?collection={collection_id}")
        return self.format_response(response)