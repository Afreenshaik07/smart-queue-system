from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, request
from flask_socketio import SocketIO
from queue_logic import get_estimated_time
from queue_manager import QueueManager
from ml_model import predict_wait_time
from notifications import send_email

# Initialize Queue Manager
manager = QueueManager()

app = Flask(__name__)
socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        current_queue = int(request.form.get("queue_length", 0))
        ml_pred = predict_wait_time(current_queue)
        return {"estimated_wait": ml_pred}
    except Exception as e:
        return {"error": str(e)}, 500


@socketio.on("join_queue")
def handle_join_queue(data):
    user_id = data.get("user_id")
    email = data.get("email")

    if not user_id or not email:
        return

    queue_num = manager.add_user(user_id, email)
    est_time = predict_wait_time(manager.queue_size())

    # Send confirmation email
    send_email(
        email,
        subject="Queue Confirmation",
        content=f"Hi {user_id}, your queue number is {queue_num}. Estimated wait time: {est_time} minutes."
    )

    # Update queue for everyone (NO broadcast=True)
    socketio.emit("queue_data", {"queue": manager.get_queue()}, to=None)

    # Only to this user
    socketio.emit("queue_confirmed", {"queue_num": queue_num, "wait": est_time})


@socketio.on("next_user")
def handle_next_user():
    removed = manager.pop_user()

    socketio.emit("queue_data", {"queue": manager.get_queue()}, to=None)

    if removed:
        send_email(
            removed["email"],
            subject="Your Turn!",
            content=f"Hi {removed['user']}, it is now your turn."
        )


@socketio.on("clear_queue")
def clear_all():
    manager.clear()
    socketio.emit("queue_data", {"queue": []}, to=None)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
