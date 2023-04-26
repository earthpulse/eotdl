import requests
from tqdm import tqdm
from pathlib import Path
import os 

class APIRepo():
    # def __init__(self, url='http://localhost:8000/'):
    def __init__(self, url='https://api.eotdl.com/'):
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

    def read_in_chunks(self, file_object, CHUNK_SIZE):
        while True:
            data = file_object.read(CHUNK_SIZE)
            if not data:
                break
            yield data
    
    def ingest_large_dataset(self, name, description, path, id_token):
        content_name = str(path)
        content_path = os.path.abspath(path)
        content_size = os.stat(content_path).st_size 
        file_object = open(content_path, "rb")
        index = 0
        offset = 0
        headers = {}
        url = self.url + 'datasets/chunk'
        data = {'name': name, 'description': description}
        id = None
        calls = 0
        for chunk in self.read_in_chunks(file_object, 1024*1024*5):
            offset = index + len(chunk)
            headers['Content-Range'] = 'bytes %s-%s/%s' % (index, offset - 1, content_size) 
            headers['Authorization'] = 'Bearer ' + id_token
            index = offset 
            file = {"file": chunk}
            if id is not None: data['id'] = id
            r = requests.post(url, files=file, headers=headers, data=data)
            if r.status_code == 200:
                id = r.json()['id']
                print("r: %s, Content-Range: %s" % (r, headers['Content-Range'])) 
            else:
                break
            calls += 1
            # if calls >= 3: break
        return r


    