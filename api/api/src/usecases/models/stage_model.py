import prometheus_client

from ...repos import OSRepo

# ValueError: Duplicated timeseries in CollectorRegistry: {'eotdl_api_downloaded_bytes_created', 'eotdl_api_downloaded_bytes', 'eotdl_api_downloaded_bytes_total'}

# eotdl_api_downloaded_bytes = prometheus_client.Counter(
#     "eotdl_api_downloaded_bytes",
#     documentation="Bytes downloaded from this api",
#     labelnames=["user_email"],
# )

def stage_model_file(model_id, filename, user, version=None):
    os_repo = OSRepo()
    if not os_repo.exists(model_id, filename):
        raise Exception(f"File `{filename}` does not exist")
    return os_repo.get_presigned_url(model_id, filename)