#%%
import openeo
import geopandas as gpd
import json
from openeo.api.process import Parameter

from openeo.rest.udp import build_process_dict
from utils import default_geojson, compute_percentiles
from s3proxy_utils import upload_geoparquet_file


##Define input parameters
temporal_extent = Parameter.temporal_interval(name="temporal_extent")
area = Parameter.geojson(name="geometry")

#Define input scl
connection=openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()

#upload the feature collection to the S3 proxy in order to use it within filter spatial
#feature_crs  = area.get("features", {})[0].get("properties", {})['crs']
#features = gpd.GeoDataFrame.from_features(area).set_crs(feature_crs)
#url = upload_geoparquet_file(features,connection)
#url = upload_geoparquet_file(area,connection)
#area = connection.load_url(url, format="Parquet")


scl = connection.load_collection(
    "SENTINEL2_L2A",
    temporal_extent=temporal_extent,
    bands=["SCL"],
    max_cloud_cover=70
).filter_spatial(area)


mask = scl.process("to_scl_dilation_mask", data=scl) 
    
##Create a composite
sentinel2 = connection.load_collection(
    "SENTINEL2_L2A",
    temporal_extent = temporal_extent,
    bands = ["B02", "B03", "B04", "B08", "B11", "B12"],
    max_cloud_cover=70
).filter_spatial(area)

sentinel2_masked = sentinel2.mask(mask)

#select the first day per month
composite = sentinel2_masked.aggregate_temporal_period(period="week", reducer="mean")

statistics = compute_percentiles(composite, [0.1, 0.25, 0.50, 0.75, 0.9])

result = statistics.save_result(format="NetCDF")

##save the process graph
process_id = "s2_bap_statistics"
connection.save_user_defined_process(
    user_defined_process_id=process_id,
    process_graph=result,
    parameters=[temporal_extent, area],
)

spec = build_process_dict(
    process_id="s2_weekly_statistics",
    process_graph=result,
    parameters=[temporal_extent, area],
)

with open("s2_weekly_statistics.json", "w") as f:
    json.dump(spec, f, indent=2)


    
