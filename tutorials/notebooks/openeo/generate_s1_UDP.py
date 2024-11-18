#%%
import openeo
from openeo.api.process import Parameter
from openeo.rest.udp import build_process_dict
import json
import geopandas as gpd

from utils import default_geojson,compute_percentiles
from s3proxy_utils import upload_geoparquet_file

["VH", "VV"]
[0.1, 0.25, 0.50, 0.75, 0.9]
##Define input parameters
temporal_extent = Parameter.temporal_interval(name="temporal_extent")
area = Parameter.geojson(name="geometry", default = default_geojson)

#Define input scl
connection=openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()

#upload the feature collection to the S3 proxy in order to use it within filter spatial
#feature_crs  = area.get("features", {})[0].get("properties", {})['crs']
#features = gpd.GeoDataFrame.from_features(area).set_crs(feature_crs)
#url = upload_geoparquet_file(area,connection)
#area = connection.load_url(url, format="Parquet")

# load collection
sentinel1 = connection.load_collection(
    collection_id="SENTINEL1_GRD",
    temporal_extent=temporal_extent,
    bands=["VH", "VV"]).filter_spatial(area)

# apply back scatter filtering
sentinel1 = sentinel1.sar_backscatter(elevation_model= "COPERNICUS_30", coefficient="sigma0-ellipsoid")

#get montly composites
composite = sentinel1.aggregate_temporal_period(period="week", reducer="mean")

statistics = compute_percentiles(composite, [0.1, 0.25, 0.50, 0.75, 0.9]
)

result = statistics.save_result(format="NetCDF")

##save the process graph
process_id = "s1_weekly_statistics"
connection.save_user_defined_process(
    user_defined_process_id=process_id,
    process_graph=result,
    parameters=[temporal_extent, area],
)

spec = build_process_dict(
    process_id="s1_weekly_statistics",
    process_graph=result,
    parameters=[temporal_extent, area],
)

with open("s1_weekly_statistics.json", "w") as f:
    json.dump(spec, f, indent=2)
