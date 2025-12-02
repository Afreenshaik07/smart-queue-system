# ml_model.py (FINAL + AUTO INITIALIZE)

from sklearn.linear_model import LinearRegression
import numpy as np
import joblib
import logging
import os

# Global model reference
wait_time_model = None

# Safe model path (Render compatible)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "wait_time_model.pkl")

logging.basicConfig(level=logging.INFO)


# ------------------------------------------------------------
# DEFAULT MODEL (always available)
# ------------------------------------------------------------
def load_default_model():
    """Creates a simple default model so Render NEVER fails."""
    global wait_time_model

    X = np.array([[1], [2], [3], [4], [5]])     # positions
    y = np.array([240, 360, 480, 600, 720])     # wait times in seconds

    model = LinearRegression()
    model.fit(X, y)

    wait_time_model = model
    logging.info("✅ Default ML wait-time model loaded.")

    return model


# ------------------------------------------------------------
# Load model from disk
# ------------------------------------------------------------
def load_wait_model(path=MODEL_PATH):
    if os.path.exists(path):
        try:
            model = joblib.load(path)
            logging.info(f"📂 ML model loaded from {path}")
            return model
        except Exception as e:
            logging.error(f"❌ Failed loading saved model: {e}")

    logging.warning("⚠ No saved model found — using default model.")
    return load_default_model()


# ------------------------------------------------------------
# Initialize model at startup
# ------------------------------------------------------------
def initialize_wait_model():
    global wait_time_model
    wait_time_model = load_wait_model()

    if wait_time_model:
        logging.info("🚀 ML model initialized successfully.")
    else:
        logging.warning("⚠ Model load failed — using default fallback.")
        load_default_model()


# ------------------------------------------------------------
# Optional: Training functions
# ------------------------------------------------------------
def prepare_training_data_from_log(wait_log):
    data = []
    for i, log in enumerate(wait_log):
        if "duration" in log:
            data.append({"position": i + 1, "wait_time": log["duration"]})
    return data


def train_wait_model(wait_log):
    data = prepare_training_data_from_log(wait_log)

    if len(data) < 2:
        logging.warning("⚠ Not enough data to train new model.")
        return None

    X = np.array([d['position'] for d in data]).reshape(-1, 1)
    y = np.array([d['wait_time'] for d in data])

    model = LinearRegression()
    model.fit(X, y)
    logging.info("🔄 Model retrained successfully.")
    return model


def save_wait_model(model, path=MODEL_PATH):
    try:
        joblib.dump(model, path)
        logging.info(f"📁 Model saved to {path}")
    except Exception as e:
        logging.error(f"❌ Model save failed: {e}")


def refresh_wait_model(wait_log):
    global wait_time_model
    new_model = train_wait_model(wait_log)

    if new_model:
        save_wait_model(new_model)
        wait_time_model = new_model
    else:
        logging.warning("⚠ Model refresh skipped (not enough data).")


# ------------------------------------------------------------
# Prediction
# ------------------------------------------------------------
def predict_wait_time(position: int):
    global wait_time_model

    if wait_time_model is None:
        logging.warning("⚠ Model missing — using fallback.")
        return 4.0

    try:
        predicted_seconds = float(wait_time_model.predict([[position]])[0])
        predicted_minutes = round(predicted_seconds / 60, 2)

        logging.info(
            f"🔮 Prediction → position {position} = {predicted_seconds:.2f} sec "
            f"({predicted_minutes} minutes)"
        )

        return predicted_minutes

    except Exception as e:
        logging.error(f"❌ Prediction error: {e}")
        return 4.0


# ------------------------------------------------------------
# 🚀 AUTO-INITIALIZE MODEL (IMPORTANT!)
# ------------------------------------------------------------
initialize_wait_model()
