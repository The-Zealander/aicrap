import argparse
import os
import tensorflow as tf
import cv2
import numpy as np
import sys

# Suppress TensorFlow logs
tf.get_logger().setLevel('ERROR')

# ===== Monkey-patch to handle legacy 'groups' arg in DepthwiseConv2D configs =====
from tensorflow.keras.layers import DepthwiseConv2D as _BaseDepthwiseConv2D

_orig_dc2d_init = _BaseDepthwiseConv2D.__init__
def _patched_dc2d_init(self, *args, groups=None, **kwargs):
    # Drop 'groups' if present (legacy from older Keras versions)
    if 'groups' in kwargs:
        kwargs.pop('groups')
    _orig_dc2d_init(self, *args, **kwargs)
_BaseDepthwiseConv2D.__init__ = _patched_dc2d_init

_orig_dc2d_from_config = _BaseDepthwiseConv2D.from_config
@classmethod
def _patched_dc2d_from_config(cls, config):
    # Remove 'groups' before deserialization
    config.pop('groups', None)
    return _orig_dc2d_from_config(config)
_BaseDepthwiseConv2D.from_config = _patched_dc2d_from_config
# =====================================================================================


def load_labels(label_path):
    with open(label_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def preprocess_frame(frame, target_shape):
    # Convert from BGR (OpenCV) to RGB (model)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # OpenCV resize wants (width, height)
    width, height = target_shape[1], target_shape[0]
    frame_resized = cv2.resize(frame_rgb, (width, height), interpolation=cv2.INTER_AREA)
    # Normalize to [-1, +1]
    img = frame_resized.astype(np.float32)
    img = (img / 127.5) - 1.0
    # Add batch dim
    return np.expand_dims(img, axis=0)



def run_inference(model, frame, labels):
    input_tensor = preprocess_frame(frame, model.input_shape[1:3])
    preds = model.predict(input_tensor)[0]
    print("Raw softmax scores:", preds)           # <-- for debugging
    idx = np.argmax(preds)
    return labels[idx], float(preds[idx])


def main(args):
    # Resolve paths relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = args.model if os.path.isabs(args.model) else os.path.join(base_dir, args.model)
    labels_path = args.labels if os.path.isabs(args.labels) else os.path.join(base_dir, args.labels)

    print(f"Loading model from {model_path}")
    model = tf.keras.models.load_model(model_path, compile=False)
    labels = load_labels(labels_path)
    print(f"Loaded {len(labels)} labels from {labels_path}")

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Error: Could not open camera index {args.camera}")
        sys.exit(1)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Frame capture failed")
                break

            class_name, confidence = run_inference(model, frame, labels)
            text = f"{class_name}: {confidence*100:.1f}%"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow("Inference", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Real-time image classification with TensorFlow and OpenCV")
    parser.add_argument("--model", type=str, default="keras_model.h5",
                        help="Path to .h5 or SavedModel directory (relative to script)")
    parser.add_argument("--labels", type=str, default="labels.txt",
                        help="Path to labels text file (relative to script)")
    parser.add_argument("--camera", type=int, default=0,
                        help="Camera device index")
    args = parser.parse_args()
    main(args)