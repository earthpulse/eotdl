#%%
import openeo

from openeo.processes import if_, is_nan
from openeo.api.process import Parameter
from openeo.rest.udp import build_process_dict
import json

from utils import compute_percentiles

from utils_BAP import (calculate_cloud_mask, calculate_cloud_coverage_score,
                           calculate_date_score, calculate_distance_to_cloud_score,
                           calculate_distance_to_cloud_score, aggregate_BAP_scores,
                           create_rank_mask)

MAX_CLOUD_PARAM = 70
SPATIAL_RESOLUTION = 20
WEIGHTS = [1, 0.8, 0.5]
PERCENTILES = [0.1, 0.25, 0.50, 0.75, 0.9]


##Define input parameters
temporal_extent = Parameter.temporal_interval(name="temporal_extent")
area = Parameter.geojson(name="geometry")

schema = {"type": "string", "enum":["B02","B03","B04","B05","B06","B07","B08","B8A","B11","B12"]}
bands_param = Parameter.array(name="bands",description="Sentinel-2 L2A bands to include in the composite.", item_schema=schema, default=["B04", "B03", "B02"], optional=True)

weight_param = Parameter.array(name="BAP_weights",description="Weights for the summed average between the distance to cloud-, date- and average score.", default=[1, 0.8, 0.5], optional=True)
percentile_param = Parameter.array(name="percentiles",description="percentiles calculated across the BAP composite.", default=[0.1, 0.25, 0.50, 0.75, 0.9], optional=True)

max_cloud_param = Parameter.integer(name="max_cloud_cover",description="Maximal cloud cover (%) used when loading in the data.", default=70, optional=True)
spatial_resolution_param = Parameter.integer(name="max_cloud_cover",description="Spatial resolution to resample the scl layer to, must match the resolution of the provided bands.", default=20, optional=True)


# Get the values provided or fall back on the default
user_bands = getattr(bands_param, 'value', bands_param.default)
user_weights = getattr(weight_param, 'value', weight_param.default)
user_percentile = getattr(percentile_param, 'value', percentile_param.default)
user_resolution = getattr(spatial_resolution_param, 'value', spatial_resolution_param.default)
user_max_cloud = getattr(max_cloud_param, 'value', max_cloud_param.default)

##Define input scl
connection=openeo.connect("openeofed.dataspace.copernicus.eu").authenticate_oidc()

scl = connection.load_collection(
    "SENTINEL2_L2A",
    temporal_extent=temporal_extent,
    bands=["SCL"],
    max_cloud_cover=user_max_cloud
).resample_spatial(user_resolution).filter_spatial(area)

scl = scl.apply(lambda x: if_(is_nan(x), 0, x))
cloud_mask =  calculate_cloud_mask(scl)

## Calculate the individual scores which will be combined in a weighted sum

#calculate the coverage score
coverage_score = calculate_cloud_coverage_score(cloud_mask, area, scl)

#datescore
date_score = calculate_date_score(scl)

#distance to cloud score
dtc_score = calculate_distance_to_cloud_score(cloud_mask, user_resolution)

##Aggregate the scores
score = aggregate_BAP_scores(dtc_score, date_score, coverage_score, user_weights)
score = score.mask(scl.band("SCL") == 0)

##Create a mask
rank_mask = create_rank_mask(score)

##Create a composite
sentinel2 = connection.load_collection(
    "SENTINEL2_L2A",
    temporal_extent = temporal_extent,
    bands = user_bands,
    max_cloud_cover=user_max_cloud
).filter_spatial(area)

#select the first day per month
composite = sentinel2.mask(rank_mask).mask(cloud_mask).aggregate_temporal_period("month","first")

statistics = compute_percentiles(composite, user_percentile)

##save the process graph
process_id = "s2_bap_statistics"
connection.save_user_defined_process(
    user_defined_process_id=process_id,
    process_graph=composite,
    parameters=[temporal_extent, area, bands_param, weight_param, percentile_param],
)

spec = build_process_dict(
    process_id="s2_bap_statistics",
    process_graph=statistics,
    parameters=[temporal_extent, area, bands_param, weight_param, percentile_param],
)

with open("s2_bap_statistics.json", "w") as f:
    json.dump(spec, f, indent=2)

#%%
import openeo
import json

connection = openeo.connect("openeofed.dataspace.copernicus.eu").authenticate_oidc()

# Load the process graph from the JSON file (if you saved it before, adapt the path)
process_graph_file = "C:\\Git_projects\\eotdl\\tutorials\\notebooks\\openeo\\eotdl_bap_statistics.json"


with open(process_graph_file, 'r') as f:
    process_graph  = json.load(f)

# Define the spatial extent
spatial_extent = dict(zip(["west", "south", "east", "north"], [664000.0, 5611120.0, 665000.0, 5612120.0]))
spatial_extent['crs'] = "EPSG:32631"

# Define the temporal extent
temporal_extent = ["2023-05-01", "2023-07-30"]

job = connection.datacube_from_json(process_graph_file,
                                    parameters = {'geometry': spatial_extent,
                                                'temporal_extent': temporal_extent})

job.execute_batch(
    outputfile="./test.nc",  # File path where NetCDF will be saved
    out_format="NetCDF",
    title="test"
)

    
