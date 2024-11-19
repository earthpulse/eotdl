#%%
import openeo
import json
from openeo.api.process import Parameter
from openeo.rest.udp import build_process_dict
from utils import compute_percentiles

##Define input parameters

spatial_extent = Parameter.bounding_box(
        name="spatial_extent", default=None, optional=True
    )
temporal_extent = Parameter.temporal_interval(name="temporal_extent")

#Define input scl
connection=openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()

scl = connection.load_collection(
    "SENTINEL2_L2A",
    spatial_extent=spatial_extent,
    temporal_extent=temporal_extent,
    bands=["SCL"],
    max_cloud_cover=75.0
)

mask = scl.process("to_scl_dilation_mask", data=scl) 
    
##Create a composite
sentinel2 = connection.load_collection(
    "SENTINEL2_L2A",
    temporal_extent = temporal_extent,
    bands = ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12"],
    max_cloud_cover=75.0)

sentinel2_masked = sentinel2.mask(mask)

#select the first day per month
composite = sentinel2_masked.aggregate_temporal_period(period="week", reducer="mean")
statistics = compute_percentiles(composite, [0.1, 0.25, 0.50, 0.75, 0.9])

##save the process graph
process_id = "s2_bap_statistics"
connection.save_user_defined_process(
    user_defined_process_id=process_id,
    process_graph=statistics,
    parameters=[temporal_extent, spatial_extent],
)

spec = build_process_dict(
    process_id="s2_weekly_statistics",
    process_graph=statistics,
    parameters=[temporal_extent, spatial_extent],
)

with open("s2_weekly_statistics.json", "w") as f:
    json.dump(spec, f, indent=2)



