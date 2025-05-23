from pathlib import Path
import requests
import os

from ..repos import APIRepo


class FilesAPIRepo(APIRepo):
    def __init__(self, url=None):
        super().__init__(url)

    def ingest_file(
        self, file_path_or_bytes, file_name, dataset_or_model_id, user, endpoint, version=None
    ):
        url = self.url + f"{endpoint}/{dataset_or_model_id}"
        if version is not None:
            url += "?version=" + str(version)
        # get a presigned url to upload the file directly to the bucket
        reponse = requests.post(
            url,
            json={
                "file_name": file_name,
                # "file_size": files_size,
                # "checksum": checksum
            },
            headers=self.generate_headers(user),
        )
        data, error = self.format_response(reponse)
        if error:
            raise Exception(error)
        # ingest the file
        error = None
        try:
            presigned_url = data["presigned_url"]
            if isinstance(file_path_or_bytes, (str, bytes)):
                if isinstance(file_path_or_bytes, str):
                    # Handle file path
                    with open(file_path_or_bytes, 'rb') as f:
                        file_data = f.read()
                else:
                    # Handle bytes directly
                    file_data = file_path_or_bytes
                # Send file data to presigned URL
                response = requests.put(presigned_url, data=file_data)
                response.raise_for_status()
            else:
                raise TypeError("file_path_or_bytes must be either a file path string or bytes")
        except Exception as e:
            error = str(e)
        return data, error

    def stage_file(
        self,
        dataset_or_model_id,
        file_name,
        user,
        path,
        endpoint="datasets",
        progress=False,
    ):
        url = self.url + f"{endpoint}/{dataset_or_model_id}/stage/{file_name}"
        # if file_version is not None:
        #     url += "?version=" + str(file_version)
        return self.stage_file_url(url, path, user)

    def stage_file_url(
        self,
        url,
        path,
        user,
    ):
        if '/stage/' in url:  # asset is in EOTDL (can do better...)
            splitted = url.split("/stage/")
            file_name = splitted[-1]
            dataset_or_model_id = splitted[0].split("/")[-1]
            response = requests.get(url, headers=self.generate_headers(user))  # fixed typo
            #print(url)
            data, error = self.format_response(response)
            #print(data)
            if error:
                raise Exception(error)
            presigned_url = data["presigned_url"]
        else:
            splitted = url.split("//")
            file_name = splitted[-1]
            dataset_or_model_id = splitted[0].split("/")[-1]
            presigned_url = url

        file_path = f"{path}/{file_name}"
        for i in range(1, len(file_path.split("/")) - 1):
            os.makedirs("/".join(file_path.split("/")[: i + 1]), exist_ok=True)

        try:
            symbolic_link = False
            cache_base_path = os.getenv("EOTDL_CACHE_PATH", "")
            if cache_base_path:
                cache_path = Path(f"{cache_base_path}/{dataset_or_model_id}/{file_name}")
                #print(cache_path)
                if cache_path.exists():
                    symbolic_link = True
                    #print(f"Using cache: {cache_path}")

            if symbolic_link:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                os.symlink(cache_path, file_path)
                #print(f"Symlinked {file_path} → {cache_path}")
            else:
                response = requests.get(presigned_url)
                response.raise_for_status()  # This will raise an HTTPError for 4XX and 5XX status codes
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                #print(f"Downloaded to: {file_path}")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Failed to stage file: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error while staging file: {str(e)}")
        return file_path
    
    def generate_presigned_url(self, filename, dataset_or_model_id, user, endpoint="datasets"):
        url = f"{self.url}{endpoint}/{dataset_or_model_id}/stage/{filename}"
        reponse = requests.get(url, headers=self.generate_headers(user))
        data, error = self.format_response(reponse)
        if error:
            # print("ERROR generate_presigned_url", error)
            return None
        return data["presigned_url"]