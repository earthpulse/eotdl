#%%
import openeo
from openeo.api.process import Parameter
from openeo.rest.udp import build_process_dict
import json
import geopandas as gpd

from utils import default_geojson,compute_percentiles
from s3proxy_utils import upload_geoparquet_file



# Extract the GeoJSON from the input parameter or use the default if not provided

##Define input parameters
temporal_extent = Parameter.temporal_interval(name="temporal_extent")
area = Parameter.geojson(name="geometry", default = default_geojson)

schema = {"type": "string", "enum":["VH", "VV"]}
bands_param = Parameter.array(name="bands",description="Sentinel-1 bands to include in the composite.", item_schema=schema, default=["VH", "VV"], optional=True)
percentile_param = Parameter.array(name="percentiles",description="percentiles calculated across the BAP composite.", default=[0.1, 0.25, 0.50, 0.75, 0.9], optional=True)

# Get the values provided or fall back on the default
user_bands = getattr(bands_param, 'value', bands_param.default)
user_percentile = getattr(percentile_param, 'value', percentile_param.default)
user_area = getattr(area, 'value', default_geojson)  

#Define input scl
connection=openeo.connect("openeofed.dataspace.copernicus.eu").authenticate_oidc()

#upload the feature collection to the S3 proxy in order to use it within filter spatial
feature_crs  = user_area.get("features", {})[0].get("properties", {})['crs']
features = gpd.GeoDataFrame.from_features(user_area).set_crs(feature_crs)
url = upload_geoparquet_file(features,connection)

# load collection
sentinel1 = connection.load_collection(
    collection_id="SENTINEL1_GRD",
    temporal_extent=temporal_extent,
    bands=user_bands).filter_spatial(connection.load_url(url, format="Parquet"))

# apply back scatter filtering
sentinel1 = sentinel1.sar_backscatter(elevation_model= "COPERNICUS_30", coefficient="sigma0-ellipsoid")

#get montly composites
composite = sentinel1.aggregate_temporal_period(period="week", reducer="mean")

statistics = compute_percentiles(composite, user_percentile)

result = statistics.save_result(format="NetCDF")

##save the process graph
process_id = "s1_weekly_statistics"
connection.save_user_defined_process(
    user_defined_process_id=process_id,
    process_graph=result,
    parameters=[temporal_extent, area, bands_param, percentile_param],
)

spec = build_process_dict(
    process_id="s1_weekly_statistics",
    process_graph=result,
    parameters=[temporal_extent, area, bands_param, percentile_param],
)

with open("s1_weekly_statistics.json", "w") as f:
    json.dump(spec, f, indent=2)
