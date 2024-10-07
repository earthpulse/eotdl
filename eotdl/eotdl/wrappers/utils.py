from ..curation.stac import STACDataFrame

def download_model(model_name, dst_path, version, force=False, download=True):
    # check if model already downloaded
    version = 1 if version is None else version
    download_path = dst_path + "/" + model_name + "/v" + str(version)
    if os.path.exists(download_path) and not force:
        df = STACDataFrame.from_stac_file(download_path + f"/{model_name}/catalog.json")
        return download_path, df
    # check model exists
    model, error = retrieve_model(model_name)
    if error:
        raise Exception(error)
    if model["quality"] < 2:
        raise Exception("Only Q2+ models are supported")
    # check version exist
    assert version in [
        v["version_id"] for v in model["versions"]
    ], f"Version {version} not found"
    # download model files
    gdf, error = retrieve_model_stac(model["id"], version)
    if error:
        raise Exception(error)
    df = STACDataFrame(gdf)
    if not download:
        return download_path, df
    os.makedirs(download_path, exist_ok=True)
    df.to_stac(download_path)
    df = df.dropna(subset=["assets"])
    for row in df.iterrows():
        for k, v in row[1]["assets"].items():
            href = v["href"]
            _, filename = href.split("/download/")
            download_file_url(href, filename, f"{download_path}/assets")
    return download_path, df