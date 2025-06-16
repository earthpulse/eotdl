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
	return np.expand_dims((image / norm_values).clip(0, 1).astype(np.float32), axis=0)

@app.post("/classification/{model}")
async def classification(
	request: Request,  
	model: str, 
	image: UploadFile = File(...), 
):
	image = load_image(image)
	outputs = inference(model, image)
	return outputs.tolist()


@app.post("/segmentation/{model}")
async def segmentation(
	request: Request,  
	model: str, 
	image: UploadFile = File(...), 
):
	image = load_image(image)
	outputs = inference(model, image)
	outputs = np.argmax(outputs[0], axis=0) + 1
	img = Image.fromarray(outputs.astype(np.uint16))  # Use uint16 to preserve integer values
	buf = io.BytesIO()
	img.save(buf, "tiff")
	buf.seek(0)
	return StreamingResponse(buf, media_type="image/tiff")
