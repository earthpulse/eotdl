from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import rasterio as rio
import io
from PIL import Image
from skimage.transform import resize
import onnxruntime
import numpy as np

MODELS_PATH = 'outputs/'

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

def load_model(model):
	ort_session = onnxruntime.InferenceSession(MODELS_PATH + model)
	return ort_session

def inference(model, image):
	ort_session = load_model(model)
	input_name = ort_session.get_inputs()[0].name
	ort_inputs = {input_name: image}
	ort_outs = ort_session.run(None, ort_inputs)
	return ort_outs[0]

def load_image(image, bands=(1,2,3), norm_values=4000):
	with rio.open(io.BytesIO(image.file.read())) as src:
		image = src.read(bands)
	return (image / norm_values).clip(0, 1).astype(np.float32)

@app.post("/{model}")
async def classification(
	request: Request,  
	model: str, 
	image: UploadFile = File(...), 
):
	image = load_image(image)
	outputs = inference(model, image)
	return outputs.tolist()


@app.post("/{model}")
async def segmentation(
	request: Request,  
	model: str, 
	image: UploadFile = File(...), 
):
    image = load_image(image)
    outputs = inference(model, image)
    if outputs.ndim == 3:  # get first band
        outputs = outputs[0]
    # outputs = resize(outputs, model_wrapper.original_size, preserve_range=True)
    # outputs = outputs.astype(np.uint8)
    img = Image.fromarray(outputs, mode="F")  # only returns binary mask
    buf = io.BytesIO()
    img.save(buf, "tiff")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/tiff") 
