import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing import image

# --- Configuration ---
MODEL_PATH = 'data/keras_model.h5'
LABELS_PATH = 'data/labels.txt'   # Ensure labels.txt is in same directory as model
IMAGE_PATH = 'testimages/images.jpg'

# --- Debugging: Check if the model file exists at the specified path ---
print(f"Checking if model file exists at: {MODEL_PATH}")
if not os.path.exists(MODEL_PATH):
    print(f"Error: Model file NOT found at {MODEL_PATH}")
    print("Please double-check the path and ensure the file is there.")
    exit()
else:
    print(f"Model file found at {MODEL_PATH}")

# --- Load labels ---
if not os.path.exists(LABELS_PATH):
    print(f"Error: Labels file NOT found at {LABELS_PATH}")
    print("Please double-check the path and ensure the file is there.")
    exit()
with open(LABELS_PATH, "r") as f:
    labels = [line.strip() for line in f.readlines()]

model = keras.models.load_model(MODEL_PATH)
# Infer required input size from the model
input_shape = model.input_shape
if isinstance(input_shape, list):  # For multi-input models
    input_shape = input_shape[0]
img_height, img_width = input_shape[1], input_shape[2]
img = image.load_img(IMAGE_PATH, target_size=(img_height, img_width))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array = img_array / 255.0  # Normalize; adjust if your model expects something different

# --- Predict ---
preds = model.predict(img_array)
preds = preds[0]  # Remove batch dimension

# Sort and print results
results = sorted(
    [{"label": labels[i], "confidence": float(conf)}
        for i, conf in enumerate(preds)],
    key=lambda x: x["confidence"],
    reverse=True
)
print(f"\nClassification results for {IMAGE_PATH}:")
for result in results:
    print(f"  Label: {result['label']}, Confidence: {result['confidence']:.4f}")

if results:
    print(f"\nTop Prediction: {results[0]['label']} with confidence {results[0]['confidence']:.4f}")