import pandas as pd
from datetime import datetime
from tqdm import tqdm
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Read file and process lines
with open('esawaai.csv', 'r') as f:
    lines = f.readlines()

# Remove leading/trailing whitespace and split on first space
data = []
for line in lines:
    line = line.strip()
    if line:  # Skip empty lines
        size, path = line.split(' ', 1)
        data.append([int(size), path])

# Convert to pandas DataFrame
df = pd.DataFrame(data, columns=['size', 'path'])
df['id'] = df.apply(lambda x: x['path'].split('/')[-1], axis=1)


def post_prr(args):
    id, path = args
    # print(id)
    response = requests.post(
        'https://eoresults.esa.int/reg-api/collections/ESAWAAI/items',
        auth=(os.getenv('PRR_USER'), os.getenv('PRR_PWD')),
        headers={
            'accept': 'application/json',
            'Content-Type': 'application/json'
        },
        json={
            "type": "Feature",
            "stac_version": "1.0.0",
            "stac_extensions": [
                "https://stac-extensions.github.io/alternate-assets/v1.1.0/schema.json",
                "https://stac-extensions.github.io/storage/v1.0.0/schema.json"
            ],
            "id": id,
            "properties": {
                "datetime": datetime.now().isoformat() + 'Z'
            },
            "assets": {
                "PRODUCT": {
                    "href": path
                }
            }
        }
    )
    # print(response.json())
    return response.json()

# from concurrent.futures import ThreadPoolExecutor

# args = [(row['id'], row['path']) for _, row in df.iterrows()]

# with ThreadPoolExecutor() as pool:
#     with tqdm(total=len(args)) as progress:
#         futures = []

#         for arg in args:
#             future = pool.submit(post_prr, arg) 
#             future.add_done_callback(lambda p: progress.update())
#             futures.append(future)

#         results = []
#         for future in futures:
#             result = future.result()
#             results.append(result)


results = []
for _, row in tqdm(df.iterrows(), total=len(df)):
    results.append(post_prr((row['id'], row['path'])))

df['result'] = results

df.to_csv('esawaai_results.csv', index=False)





