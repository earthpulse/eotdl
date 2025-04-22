import pandas as pd

from ..datasets.retrieve_dataset import retrieve_dataset
from ..models.retrieve_model import retrieve_model
from ...repos import OSRepo
from ...errors import DatasetDoesNotExistError

def retrieve_stac_items(collection_id, version):
    try:
        data = retrieve_dataset(collection_id)
    except DatasetDoesNotExistError:
        data = retrieve_model(collection_id)
    os_repo = OSRepo()
    catalog_presigned_url = os_repo.get_presigned_url(data.id, f"catalog.v{version}.parquet")
    # this read the entire catalog into memory, which is not ideal
    df = pd.read_parquet(catalog_presigned_url)
    return [
        {
            "id": row["id"],
            "assets": row["assets"],
        }
        for _, row in df.iterrows()
    ]