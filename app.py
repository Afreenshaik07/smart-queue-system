from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
from queue_manager import manager
from ml_model import predict_wait_time
from notifications import send_email
import logging

app = Flask(__name__)
socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")

logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------
# ROOT PAGE
# ---------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------
# JOIN QUEUE (HTTP API)
# ---------------------------------------------------
@app.route("/join", methods=["POST"])
def join_queue():
    data = request.json
    user_id = data.get("user_id")
    email = data.get("email")

    position = manager.add_user(user_id, email)
    wait_minutes = predict_wait_time(position)

    # Expected serve time
    expected_time = datetime.now() + timedelta(minutes=wait_minutes)
    serve_by = expected_time.strftime("%I:%M %p")

    # Send email
    send_email(
        to_email=email,
        subject="Queue Confirmation",
        body=f"Hi {user_id},\nYou joined the queue.\nYour position: {position}\nEstimated wait: {wait_minutes} minutes\nExpected serve time: {serve_by}"
    )

    socketio.emit("queue_data", {"queue": manager.get_queue()})
    return jsonify({"position": position, "wait": wait_minutes})


# ---------------------------------------------------
# SOCKET.IO — Client Connected
# ---------------------------------------------------
@socketio.on("connect")
def handle_connect():
    logging.info("✅ Client connected.")
    emit("queue_data", {"queue": manager.get_queue()})


# ---------------------------------------------------
# SOCKET.IO — Get Queue
# ---------------------------------------------------
@socketio.on("get_queue")
def handle_get_queue():
    emit("queue_data", {"queue": manager.get_queue()})


# ---------------------------------------------------
# SOCKET.IO — User Joins Queue
# ---------------------------------------------------
@socketio.on("join_queue")
def handle_join_queue(data):
    user_id = data["user_id"]
    email = data["email"]

    logging.info(f"👋 Join request received: {user_id}")

    position = manager.add_user(user_id, email)
    wait_minutes = predict_wait_time(position)

    expected_time = datetime.now() + timedelta(minutes=wait_minutes)
    serve_by = expected_time.strftime("%I:%M %p")

    # Send email (via SendGrid)
    send_email(
        to_email=email,
        subject="Queue Confirmation",
        body=f"Hi {user_id},\nYou joined the queue.\nYour position: {position}\nEstimated wait: {wait_minutes} minutes\nExpected serve time: {serve_by}"
    )

    emit("position_updated", {
        "user_id": user_id,
        "position": position,
        "estimated_wait": wait_minutes,
    })

    socketio.emit("queue_data", {"queue": manager.get_queue()}, broadcast=True)


# ---------------------------------------------------
# SOCKET.IO — Next User
# ---------------------------------------------------
@socketio.on("next_user")
def handle_next_user():
    served = manager.pop_user()

    if served:
        socketio.emit("now_serving", {"user_id": served["user_id"]}, broadcast=True)
        socketio.emit("queue_data", {"queue": manager.get_queue()}, broadcast=True)
    else:
        socketio.emit("now_serving", {"user_id": None}, broadcast=True)


# ---------------------------------------------------
# SOCKET.IO — Disconnect
# ---------------------------------------------------
@socketio.on("disconnect")
def handle_disconnect():
    logging.info("❌ Client disconnected")


# ---------------------------------------------------
# RUN (Local Only)
# ---------------------------------------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
