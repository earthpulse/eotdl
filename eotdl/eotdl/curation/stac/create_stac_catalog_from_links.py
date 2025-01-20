from pathlib import Path
import pystac
from datetime import datetime

def create_stac_catalog_from_links(path, metadata, links):

	folder = Path(path)

	# Create catalog
	catalog = pystac.Catalog(
		id=metadata.name,
		title=metadata.name,
		description="STAC catalog",
		extra_fields={
			"eotdl": {
				"name": metadata.name,
				"license": metadata.license,
				"source": metadata.source,
				"thumbnail": metadata.thumbnail,
				"authors": metadata.authors,
				"description": metadata.description
			}
		}
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

	# TODO: explore ways to infere spatial and temporal extent from the data or ask to user, otherwise use the default values

	# Add collection to catalog
	catalog.add_child(collection)

	# items
	for link in links:
		item = pystac.Item(
			id=link.split("/")[-1],
			geometry=None,
			bbox=[-180, -90, 180, 90],
			datetime=datetime.now(),
			properties={}
		)

		# add file asset
		item.add_asset(
			key=link.split("/")[-1],
			asset=pystac.Asset(
				href=link,
				media_type="application/octet-stream"
			)
		)

		# add item to collection
		collection.add_item(item)

	# Save catalog and collection as JSON files
	catalog.normalize_and_save(
	    root_href=str(folder.absolute()),
	    catalog_type=pystac.CatalogType.SELF_CONTAINED
	)

	return catalog
	