import pandas as pd
import stac_geoparquet
import pyarrow.parquet as pq
from tqdm import tqdm
import pystac

from ..datasets.retrieve_dataset import retrieve_dataset_by_name
from ..models.retrieve_model import retrieve_model_by_name
from ..pipelines.retrieve_pipeline import retrieve_pipeline_by_name
from ...repos import OSRepo
from ...errors import DatasetDoesNotExistError, ModelDoesNotExistError

def retrieve_stac_items(collection_name, version):
    try:
        data = retrieve_dataset_by_name(collection_name)
    except DatasetDoesNotExistError:
        try:
            data = retrieve_model_by_name(collection_name)
        except ModelDoesNotExistError:
            data = retrieve_pipeline_by_name(collection_name)
    os_repo = OSRepo()
    catalog_presigned_url = os_repo.get_presigned_url(data.id, f"catalog.v{version}.parquet")
    table = pq.read_table(catalog_presigned_url)
    items = []
    for item in tqdm(stac_geoparquet.arrow.stac_table_to_items(table), total=len(table)):
        item = pystac.Item.from_dict(item)
        items.append(item)
    return items