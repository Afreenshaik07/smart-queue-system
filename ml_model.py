import joblib
import logging
import os

MODEL_PATH = "wait_time_model.pkl"

# Load model
try:
    model = joblib.load(MODEL_PATH)
    logging.info("🚀 Model loaded successfully.")
except Exception as e:
    logging.error(f"⚠ Failed to load model: {e}")
    model = None


def predict_wait_time(queue_length):
    try:
        if model:
            pred = model.predict([[queue_length]])[0]
            return round(float(pred), 2)
        else:
            return queue_length * 2  # fallback simple rule
    except Exception:
        return queue_length * 2
