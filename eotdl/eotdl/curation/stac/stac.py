import pyarrow.parquet as pq
import stac_geoparquet
import json
from tqdm import tqdm
import pystac
from datetime import datetime

def create_stac_catalog(parquet_catalog_path, stac_catalog = None):
	# parse items and add to collection
	table = pq.read_table(parquet_catalog_path)
	items = []
	for item in tqdm(stac_geoparquet.arrow.stac_table_to_items(table), total=len(table)):
		item = pystac.Item.from_dict(item)
		# item.validate()
		# collection.add_item(item)
		if stac_catalog is not None:
			stac_catalog.add_item(item)
		else:
			items.append(item)
		# path = "data/stac/" + item["id"] + ".json"
		# os.makedirs(os.path.dirname(path), exist_ok=True)
		# with open(path, "w") as f:
		# 	json.dump(item, f)
		# # save item
		# os.makedirs(path, exist_ok=True)
		# _path = path + '/' + item.id + ".json"
		# os.makedirs(os.path.dirname(_path), exist_ok=True)
		# with open(_path, "w") as f:
		# 	json.dump(item.to_dict(), f)
	# save catalog
	if stac_catalog is not None:
		return stac_catalog
	return items