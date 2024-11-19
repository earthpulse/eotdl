#%%
import openeo
import json
from openeo.api.process import Parameter
from openeo.rest.udp import build_process_dict
from utils import compute_percentiles

#Define input parameters
temporal_extent = Parameter.temporal_interval(name="temporal_extent")

spatial_extent = Parameter.bounding_box(
        name="spatial_extent", default=None, optional=True
        )

#Define input scl
connection=openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()

# load collection
sentinel1 = connection.load_collection(
    collection_id="SENTINEL1_GRD",
    temporal_extent=temporal_extent,
    bands=["VH", "VV"])

# apply back scatter filtering
sentinel1 = sentinel1.sar_backscatter(elevation_model= "COPERNICUS_30", coefficient="sigma0-ellipsoid")

#get montly composites
composite = sentinel1.aggregate_temporal_period(period="week", reducer="mean")

statistics = compute_percentiles(composite, [0.1, 0.25, 0.50, 0.75, 0.9]).filter_bbox(spatial_extent)

##save the process graph
process_id = "s1_weekly_statistics"
connection.save_user_defined_process(
    user_defined_process_id=process_id,
    process_graph=statistics,
    parameters=[temporal_extent, spatial_extent],
)

spec = build_process_dict(
    process_id="s1_weekly_statistics",
    process_graph=statistics,
    parameters=[temporal_extent,spatial_extent],
)

with open("s1_weekly_statistics.json", "w") as f:
    json.dump(spec, f, indent=2)
