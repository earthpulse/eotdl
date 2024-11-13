#%%
import openeo

from openeo.api.process import Parameter
from openeo.rest.udp import build_process_dict
from utils import compute_percentiles
import json

##Define input parameters
temporal_extent = Parameter.temporal_interval(name="temporal_extent")
area = Parameter.geojson(name="geometry")

schema = {"type": "string", "enum":["B02","B03","B04","B05","B06","B07","B08","B8A","B11","B12"]}
bands_param = Parameter.array(name="bands",description="Sentinel-2 L2A bands to include in the composite.", item_schema=schema, default=["B04", "B03", "B02"], optional=True)

percentile_param = Parameter.array(name="percentiles",description="percentiles calculated across the BAP composite.", default=[0.1, 0.25, 0.50, 0.75, 0.9], optional=True)

max_cloud_param = Parameter.integer(name="max_cloud_cover",description="Maximal cloud cover (%) used when loading in the data.", default=70, optional=True)


# Get the values provided or fall back on the default
user_bands = getattr(bands_param, 'value', bands_param.default)
user_percentile = getattr(percentile_param, 'value', percentile_param.default)
user_max_cloud = getattr(max_cloud_param, 'value', max_cloud_param.default)

##Define input scl
connection=openeo.connect("openeofed.dataspace.copernicus.eu").authenticate_oidc()

scl = connection.load_collection(
    "SENTINEL2_L2A",
    temporal_extent=temporal_extent,
    bands=["SCL"],
    max_cloud_cover=user_max_cloud
).filter_spatial(area)


mask = scl.process("to_scl_dilation_mask", data=scl) 
    
##Create a composite
sentinel2 = connection.load_collection(
    "SENTINEL2_L2A",
    temporal_extent = temporal_extent,
    bands = user_bands,
    max_cloud_cover=user_max_cloud
).filter_spatial(area)

sentinel2_masked = sentinel2.mask(mask)

#select the first day per month
composite = sentinel2_masked.aggregate_temporal_period(period="week", reducer="mean")

statistics = compute_percentiles(composite, user_percentile)

result = statistics.save_result(format="NetCDF")

##save the process graph
process_id = "s2_bap_statistics"
connection.save_user_defined_process(
    user_defined_process_id=process_id,
    process_graph=result,
    parameters=[temporal_extent, area, bands_param, percentile_param],
)

spec = build_process_dict(
    process_id="s2_weekly_statistics",
    process_graph=result,
    parameters=[temporal_extent, area, bands_param, percentile_param],
)

with open("s2_weekly_statistics.json", "w") as f:
    json.dump(spec, f, indent=2)


    
