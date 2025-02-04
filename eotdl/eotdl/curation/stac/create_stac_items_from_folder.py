from datetime import datetime
from pathlib import Path
import pystac
from glob import glob
import os
import json

def create_stac_items_from_folder(folder, metadata):
	folder = Path(folder)
	
	# # Create catalog
	# catalog = pystac.Catalog(
	# 	id=metadata.name,
	# 	title=metadata.name,
	# 	description="STAC catalog",
	# 	extra_fields={
	# 		"eotdl": {
	# 			"name": metadata.name,
	# 			"license": metadata.license,
	# 			"source": metadata.source,
	# 			"thumbnail": metadata.thumbnail,
	# 			"authors": metadata.authors,
	# 			"description": metadata.description
	# 		}
	# 	}
	# )
	
	# # Create collection
	# collection = pystac.Collection(
	# 	id=f"collection",
	# 	description="description",
	# 	extent=pystac.Extent(
	# 		spatial=pystac.SpatialExtent(bboxes=[-180, -90, 180, 90]),
	# 		temporal=pystac.TemporalExtent(intervals=[[datetime.now(), None]])
	# 	),
	# 	title="collection"
	# )

	# TODO: explore ways to infere spatial and temporal extent from the data, otherwise use the default values
	
	# Add collection to catalog
	# catalog.add_child(collection)
	
	# Create items for each file in the folder
	files = glob(str(folder) + '/**/*', recursive=True)
	os.makedirs(str(folder) + '/stac', exist_ok=True)
	for file_path in files:
		file_path = Path(file_path)
		if file_path.is_file():
			item = pystac.Item(
				id=file_path.name,
				geometry=None,  # infere from data if possible
				bbox=[-180, -90, 180, 90], # infere from data if possible
				datetime=datetime.fromtimestamp(file_path.stat().st_mtime), # infere from data if possible
				properties={}
			)
			
			# Calculate relative path from item location to asset
			# Item will be stored in collection/filename/filename.json
			# item_dir = folder / "collection" / file_path.name
			item_dir = folder / file_path.name
			relative_path = Path(os.path.relpath(file_path, item_dir))
			
			# Add the file as an asset
			item.add_asset(
				key=file_path.name,
				asset=pystac.Asset(
					href=str(relative_path),
					media_type=f"application/{file_path.suffix[1:]}"  # Simple media type inference
				)
			)

			# save item to folder
			# item.save(item_dir / f"{file_path.name}.json")
			with open(str(folder) + '/stac/' + file_path.name + '.json', "w") as f:
				f.write(json.dumps(item.to_dict()))

	# 		# Add item to collection
	# 		collection.add_item(item)
	
	# # Save catalog and collection as JSON files
	# catalog.normalize_and_save(
	#     root_href=str(folder.absolute()),
	#     catalog_type=pystac.CatalogType.SELF_CONTAINED
	# )
	
	# return catalog

	return folder