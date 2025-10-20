from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras import layers, regularizers
import tensorflow_hub as hub
import tensorflow as tf
from PIL import Image
import io

app = FastAPI()

class SEBlock(layers.Layer):
    def __init__(self, ratio=16, **kwargs):
        super(SEBlock, self).__init__(**kwargs)
        self.ratio = ratio

    def build(self, input_shape):
        self.channels = input_shape[-1]
        self.global_pool = layers.GlobalAveragePooling2D()
        self.fc1 = layers.Dense(self.channels // self.ratio, activation='swish')
        self.fc2 = layers.Dense(self.channels, activation='sigmoid')
        self.reshape = layers.Reshape((1, 1, self.channels))

    def call(self, inputs):
        se = self.global_pool(inputs)
        se = self.fc1(se)
        se = self.fc2(se)
        se = self.reshape(se)
        return inputs * se

class Avg2MaxPooling(layers.Layer):
    def __init__(self, pool_size=3, strides=2, padding='same', **kwargs):
        super(Avg2MaxPooling, self).__init__(**kwargs)
        self.avg_pool = layers.AveragePooling2D(pool_size, strides, padding)
        self.max_pool = layers.MaxPooling2D(pool_size, strides, padding)
        self.bn = layers.BatchNormalization()

    def call(self, inputs):
        x = self.avg_pool(inputs) - 2 * self.max_pool(inputs)
        return self.bn(x)

class DepthwiseSeparableConv(layers.Layer):
    def __init__(self, filters, kernel_size=3, strides=1, se_ratio=16, reg=0.001, **kwargs):
        super(DepthwiseSeparableConv, self).__init__(**kwargs)
        self.dw = layers.DepthwiseConv2D(kernel_size, strides, padding='same',
                                         depthwise_regularizer=regularizers.l2(reg))
        self.pw = layers.Conv2D(filters, 1, strides=1, kernel_regularizer=regularizers.l2(reg))
        self.bn = layers.BatchNormalization()
        self.se = SEBlock(se_ratio)
        self.proj = layers.Conv2D(filters, 1, strides=1,
                                  kernel_regularizer=regularizers.l2(reg)) if strides != 1 else None

    def call(self, inputs):
        residual = inputs
        x = self.dw(inputs)
        x = self.pw(x)
        x = self.bn(x)
        x = tf.nn.swish(x)
        x = self.se(x)
        if self.proj is not None:
            residual = self.proj(residual)
        return x + residual if residual.shape == x.shape else x


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

model_path = "thyroid_cancer_model.h5"
model = tf.keras.models.load_model(
    model_path,
    compile = False,
    custom_objects={
        "KerasLayer": hub.KerasLayer,
        "SEBlock": SEBlock,
        "Avg2MaxPooling": Avg2MaxPooling,
        "DepthwiseSeparableConv": DepthwiseSeparableConv
    }
)

IMG_SIZE = (224, 224)
def preprocess_image(image_bytes):
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB (handles RGBA, grayscale, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize
        image = image.resize(IMG_SIZE, Image.LANCZOS)
        
        # Convert to array and normalize
        image_array = np.array(image).astype("float32") / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    except Exception as e:
        raise Exception(f"Image preprocessing failed: {str(e)}")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Read file contents
        contents = await file.read()
        print(f"File received: {file.filename}, size: {len(contents)} bytes")
        
        # Validate file contents
        if len(contents) == 0:
            return JSONResponse(status_code=400, content={"error": "Empty file received"})
        
        # Preprocess image
        try:
            image = preprocess_image(contents)
            print(f"Image preprocessed successfully, shape: {image.shape}")
        except Exception as img_error:
            print(f"Image preprocessing error: {str(img_error)}")
            return JSONResponse(status_code=400, content={"error": f"Invalid image format: {str(img_error)}"})

        # Make prediction
        try:
            prediction = model.predict(image)[0][0]
            print(f"Prediction value: {prediction}")
        except Exception as pred_error:
            print(f"Prediction error: {str(pred_error)}")
            return JSONResponse(status_code=500, content={"error": f"Model prediction failed: {str(pred_error)}"})

        label = "Malignant" if prediction >= 0.5 else "Benign"
        return {"label": label, "probability": float(prediction)}
        
    except Exception as e:
        print(f"General error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

