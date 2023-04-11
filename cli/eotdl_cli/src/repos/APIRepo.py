import requests
from tqdm import tqdm
from pathlib import Path
import os 

class APIRepo():
    def __init__(self, url='http://localhost:8000/'):
        self.url = url

    def login(self):
        return requests.get(self.url + 'auth/login')
    
    def token(self, code):
        return requests.get(self.url + 'auth/token?code=' + code)

    def logout_url(self):
        response = requests.get(self.url + 'auth/logout')
        return response.json()['logout_url']
    
    def retrieve_datasets(self):
        return requests.get(self.url + 'datasets').json()

    def retrieve_dataset(self, name):
        return requests.get(self.url + 'datasets?name=' + name)
    
    def download_dataset(self, dataset_id, id_token, path):
        url = self.url + 'datasets/' + dataset_id + '/download'
        headers={'Authorization': 'Bearer ' + id_token}
        if path is None:
            path = str(Path.home()) + '/.etodl/datasets'
            os.makedirs(path, exist_ok=True)
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
            filename = r.headers.get('content-disposition').split('filename=')[1][1:-1]
            path = f'{path}/{filename}'
            with open(path, 'wb') as f:
                for chunk in r.iter_content(block_size):
                    progress_bar.update(len(chunk))
                    f.write(chunk)
            progress_bar.close()
            return path
        
    def ingest_dataset(self, name, description, path, id_token):
        # Not sure this will work with large datasets, need to test
        url = self.url + 'datasets'
        headers={'Authorization': 'Bearer ' + id_token}
        files = {'file': open(path, 'rb')}
        data = {'name': name, 'description': description}
        response = requests.post(url, headers=headers, files=files, data=data)
        return response