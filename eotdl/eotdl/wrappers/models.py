# Q1+ model wrapper
# only works with some models, extend as we include more models in EOTDL and improve MLM extension

import os 
from pathlib import Path
from tqdm import tqdm
import numpy as np

from ..models.retrieve import retrieve_model
from ..curation.stac import STACDataFrame
from ..repos import FilesAPIRepo, ModelsAPIRepo
from ..auth import with_auth

class ModelWrapper:
    def __init__(self, model_name, version=None, path=None, force=False, assets=True, verbose=True):
        self.model_name = model_name
        self.version = version
        self.path = path
        self.force = force
        self.assets = assets
        self.verbose = verbose
        self.ready = False
        self.setup()

    def setup(self):
        download_path, gdf = self.download()
        self.download_path = download_path
        self.gdf = gdf
        # get model name from stac metadata
        item = gdf[gdf['type'] == "Feature"]
        assert item.shape[0] == 1, "Only one item is supported in stac metadata, found " + str(item.shape[0])
        self.props = item.iloc[0].properties
        assert self.props["mlm:framework"] == "ONNX", "Only ONNX models are supported, found " + self.props["mlm:framework"]
        model_name = self.props["mlm:name"]
        self.model_path = download_path + '/assets/' + model_name
        self.ready = True

    def predict(self, x):
        if not self.ready:
            self.setup()
        ort_session = self.get_onnx_session(self.model_path)
        # preprocess input
        x = self.process_inputs(x)
        # execute model
        input_name = ort_session.get_inputs()[0].name
        ort_inputs = {input_name: x}
        ort_outs = ort_session.run(None, ort_inputs)
        output_nodes = ort_session.get_outputs()
        output_names = [node.name for node in output_nodes]
        # format and return outputs
        return self.return_outputs(ort_outs, output_names)

    @with_auth
    def download(self, user=None):
        # download the model
        model = retrieve_model(self.model_name)
        if model["quality"] == 0:
            raise Exception("Only Q1+ models are supported")
        if self.version is None:
            self.version = sorted(model["versions"], key=lambda v: v["version_id"])[-1][
                "version_id"
            ]
        else:
            assert self.version in [
                v["version_id"] for v in model["versions"]
            ], f"Version {self.version} not found"
        download_base_path = os.getenv(
            "EOTDL_DOWNLOAD_PATH", str(Path.home()) + "/.cache/eotdl/models"
        )
        if self.path is None:
            download_path = download_base_path + "/" + self.model_name + "/v" + str(self.version)
        else:
            download_path = self.path + "/" + self.model_name + "/v" + str(self.version)
        # check if model already exists
        if os.path.exists(download_path) and not self.force:
            os.makedirs(download_path, exist_ok=True)
            gdf = STACDataFrame.from_stac_file(download_path + f"/{self.model_name}/catalog.json")
            return download_path, gdf
        if self.verbose:
            print("Downloading STAC metadata...")
        repo = ModelsAPIRepo()
        gdf, error = repo.download_stac(
            model["id"],
            user,
        )
        if error:
            raise Exception(error)
        df = STACDataFrame(gdf)
        # df.geometry = df.geometry.apply(lambda x: Polygon() if x is None else x)
        df.to_stac(download_path)
        # download assets
        if self.assets:
            if self.verbose:
                print("Downloading assets...")
            repo = FilesAPIRepo()
            df = df.dropna(subset=["assets"])
            for row in tqdm(df.iterrows(), total=len(df)):
                for k, v in row[1]["assets"].items():
                    href = v["href"]
                    _, filename = href.split("/download/")
                    # will overwrite assets with same name :(
                    repo.download_file_url(
                        href, filename, f"{download_path}/assets", user
                    )
        else:
            print("To download assets, set assets=True.")
        if self.verbose:
            print("Done")
        return download_path, gdf

    def process_inputs(self, x):
        # pre-process and validate input
        input = self.props["mlm:input"]
        # input data type
        dtype = input["input"]["data_type"]
        x = x.astype(dtype)
        # input shape
        input_shape = input["input"]["shape"]
        ndims = len(input_shape)
        if ndims != x.ndim:
            if ndims == 4:
                x = np.expand_dims(x, axis=0).astype(np.float32)
            else:
                raise Exception("Input shape not valid", input_shape, x.ndim)
        for i, dim in enumerate(input_shape):
            if dim != -1:
                assert dim == x.shape[i], f"Input dimension not valid: The model expects {input_shape} but input has {x.shape} (-1 means any dimension)."
        # TODO: should apply normalization if defined in metadata
        return x
    
    def return_outputs(self, ort_outputs, output_names):
        if self.props["mlm:output"]["tasks"] == ["classification"]:
            return {
                "model": self.model_name,
                **{
                    output: ort_outputs[i].tolist() for i, output in enumerate(output_names)
                },
            }
        elif self.props["mlm:output"]["tasks"] == ["segmentation"]:
            outputs = {output: ort_outputs[i] for i, output in enumerate(output_names)}
            batch = outputs[output_names[0]]
            image = batch[0]
            return image
        else:
            raise Exception("Output task not supported:", self.props["mlm:output"]["tasks"])

    def get_onnx_session(self, model):        
        try:
            import onnxruntime as ort
            # gpu requires `pip install onnxruntime-gpu` but no extra imports
        except ImportError:
            raise ImportError("onnxruntime is not installed. Please install it with `pip install onnxruntime`")
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        try:
            session = ort.InferenceSession(model, providers=providers)
        except Exception as e:
            raise RuntimeError(f"Error loading ONNX model: {str(e)}")
        return session
