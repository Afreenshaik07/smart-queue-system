# ruff: noqa

from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template
from flask_socketio import SocketIO
from queue_manager import QueueManager
from ml_model import predict_wait_time
from notifications import send_email

app = Flask(__name__)
socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")

manager = QueueManager()


@app.route("/")
def home():
    return render_template("index.html")


@socketio.on("join_queue")
def handle_join_queue(data):
    user_id = data.get("user_id")
    email = data.get("email")

    manager.add_user(user_id, email)
    queue = manager.get_queue()

    socketio.emit("queue_data", {"queue": queue})

    send_email(
        email,
        "Queue Joined",
        f"Hello {user_id}, your position is {len(queue)}."
    )

    wait = predict_wait_time(len(queue))
    socketio.emit("wait_time", {"minutes": wait})


@socketio.on("next_person")
def handle_next_person():
    removed = manager.pop_user()
    queue = manager.get_queue()

    socketio.emit("queue_data", {"queue": queue})

    if removed:
        send_email(
            removed["email"],
            "It's Your Turn!",
            "Please proceed to the counter now."
        )


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=10000)
