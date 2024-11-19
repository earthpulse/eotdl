#%%
import openeo
import geopandas as gpd
import json
from openeo.api.process import Parameter

from openeo.rest.udp import build_process_dict
from utils import compute_percentiles

##Define input parameters
temporal_extent = Parameter.temporal_interval(name="temporal_extent")

spatial_extent = Parameter.bounding_box(
        name="spatial_extent", default=None, optional=True
    )
temporal_extent = Parameter.temporal_interval(name="temporal_extent")


max_cloud_description = """The maximum cloud cover percentage to filter Sentinel-2 inputs at full product level.
By reducing the percentage, fewer input products are considered, which also potentially increases the risk of missing valid data.
We do not recommend setting it higher than 95%, as this decreases performance by reading very cloudy areas with little chance of finding good pixels.

For composites over large time ranges, a reduced value can help to consider only good quality input products, with few undetected clouds.
"""

max_cloud_cover_param = Parameter.number(
    name="max_cloud_cover",
    description=max_cloud_description,
    default=75.0,
    optional=True,
)
area = Parameter.geojson(name="geometry")

#Define input scl
connection=openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()

scl = connection.load_collection(
    "SENTINEL2_L2A",
    temporal_extent=temporal_extent,
    bands=["SCL"],
    max_cloud_cover=max_cloud_cover_param
)

mask = scl.process("to_scl_dilation_mask", data=scl) 
    
##Create a composite
sentinel2 = connection.load_collection(
    "SENTINEL2_L2A",
    temporal_extent = temporal_extent,
    bands = ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12"],
    max_cloud_cover=max_cloud_cover_param)

sentinel2_masked = sentinel2.mask(mask)

#select the first day per month
composite = sentinel2_masked.aggregate_temporal_period(period="week", reducer="mean")
statistics = compute_percentiles(composite, [0.1, 0.25, 0.50, 0.75, 0.9]).filter_bbox(spatial_extent)

##save the process graph
process_id = "s2_bap_statistics"
connection.save_user_defined_process(
    user_defined_process_id=process_id,
    process_graph=statistics,
    parameters=[temporal_extent, spatial_extent, max_cloud_cover_param],
)

spec = build_process_dict(
    process_id="s2_weekly_statistics",
    process_graph=statistics,
    parameters=[temporal_extent, spatial_extent, max_cloud_cover_param],
)

with open("s2_weekly_statistics.json", "w") as f:
    json.dump(spec, f, indent=2)



