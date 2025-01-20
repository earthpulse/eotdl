from datetime import datetime
from pathlib import Path
import json
import pystac
from glob import glob
import uuid

def create_stac_catalog_from_folder(folder, metadata, content):
	folder = Path(folder)
	
	# Create catalog
	catalog = pystac.Catalog(
		id=metadata.name,
		description=content,
		title=metadata.name
	)
	
	# Create collection
	collection = pystac.Collection(
		id=f"collection",
		description="description",
		extent=pystac.Extent(
			spatial=pystac.SpatialExtent(bboxes=[-180, -90, 180, 90]),
			temporal=pystac.TemporalExtent(intervals=[[datetime.now(), None]])
		),
		title="collection"
	)

	# TODO: explore ways to infere spatial and temporal extent from the data, otherwise use the default values
	
	# # Add collection to catalog
	catalog.add_child(collection)
	
	# Create items for each file in the folder
	files = glob(str(folder) + '/**/*', recursive=True)
	for file_path in files:
		file_path = Path(file_path)
		if file_path.is_file():
			item = pystac.Item(
				id=file_path.stem,
				geometry=None,  # infere from data if possible
				bbox=[-180, -90, 180, 90], # infere from data if possible
				datetime=datetime.fromtimestamp(file_path.stat().st_mtime), # infere from data if possible
				properties={}
			)
			
			# Add the file as an asset
			item.add_asset(
				key=file_path.name,
				asset=pystac.Asset(
					href=str(file_path),
					media_type=f"application/{file_path.suffix[1:]}"  # Simple media type inference
				)
			)

			# make path relative to the catalog
			item.set_self_href(str(file_path.relative_to(folder)))
			
			# Add item to collection
			collection.add_item(item)
	
	# # Save catalog and collection as JSON files
	catalog.normalize_and_save(
	    root_href=str(folder),
	    catalog_type=pystac.CatalogType.SELF_CONTAINED
	)
	
	return catalog