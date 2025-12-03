# ml_model.py - FINAL FIXED VERSION

import joblib
import os
import logging

MODEL_PATH = os.path.join(os.path.dirname(__file__), "wait_time_model.pkl")

model = None

def load_model():
    """Load ML model from file once and reuse it."""
    global model
    if model is None:
        logging.info(f"📂 Loading model from {MODEL_PATH}")
        model = joblib.load(MODEL_PATH)
        logging.info("🚀 Model loaded successfully.")
    return model

def predict_wait_time(position):
    """Predict wait time based on the queue position."""
    mdl = load_model()
    prediction = mdl.predict([[position]])
    return float(prediction[0])
