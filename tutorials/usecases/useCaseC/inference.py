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
	ds = rio.open(io.BytesIO(image.file.read())) 
	image = ds.read(bands)
	return ds, np.expand_dims((image / norm_values).clip(0, 1).astype(np.float32), axis=0)

@app.post("/classification/{model}")
async def classification(
	request: Request,  
	model: str, 
	image: UploadFile = File(...), 
):
	_, image = load_image(image)
	outputs = inference(model, image)
	return outputs[0].tolist()


@app.post("/segmentation/{model}")
async def segmentation(
	request: Request,  
	model: str, 
	image: UploadFile = File(...), 
):
	ds, image = load_image(image)
	outputs = inference(model, image)
	outputs = np.argmax(outputs[0], axis=0) + 1
	meta = ds.meta
	meta.update(count=1, dtype=np.uint8)
	
	# Create a BytesIO buffer to write the TIFF
	buf = io.BytesIO()
	with rio.open(buf, 'w', **meta) as dst:
		dst.write(outputs[np.newaxis, ...])
	
	# Reset buffer position to start
	buf.seek(0)
	
	# Return the buffer contents as a streaming response
	return StreamingResponse(buf, media_type="image/tiff")
