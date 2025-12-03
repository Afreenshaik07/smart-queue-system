# app.py - FINAL FULL WORKING VERSION WITH SENDGRID

from flask import Flask, render_template, request
import logging
from queue_manager import QueueManager
from ml_model import load_model, predict_wait_time
from notifications import send_email

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

queue = QueueManager()
model = load_model()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/join", methods=["GET", "POST"])
def join_queue():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        # Add user to queue
        user_id = queue.add_user(name)
        position = queue.get_position(user_id)

        # Predict wait time using ML
        wait_time = predict_wait_time(model, position)

        # Send Email Notification
        subject = "SmartQueue – You Joined the Queue"
        body = (
            f"Hi {name},\n\n"
            f"You are successfully added to the queue.\n\n"
            f"Your Position: {position}\n"
            f"Estimated Wait Time: {wait_time:.1f} minutes\n\n"
            f"Thanks for using SmartQueue ❤️"
        )

        send_email(email, subject, body)

        return render_template(
            "joined.html",
            name=name,
            position=position,
            wait_time=wait_time,
        )

    return render_template("join.html")


@app.route("/admin")
def admin_page():
    return render_template("admin.html")


if __name__ == "__main__":
    app.run()
