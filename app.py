# app.py (Render-Safe + ML Model Integrated)

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime, timezone, timedelta
from notifications import send_email

# --- ML imports ---
from ml_model import initialize_wait_model, predict_wait_time, refresh_wait_model

# -------------------------------------------------------
# BASIC FLASK SETUP
# -------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-truly-secret-key-that-is-safe'

# -------------------------------------------------------
# 🔥 FINAL FIX FOR RENDER — POLLING ONLY, NO WEBSOCKETS
# -------------------------------------------------------
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",         # No eventlet / gevent
    allow_upgrades=False,           # WebSocket upgrade disabled
    transports=["polling"],         # Polling ONLY
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

logging.basicConfig(level=logging.INFO)

# -------------------------------------------------------
# DATA STORAGE
# -------------------------------------------------------
QUEUE = []
NOW_SERVING = None
ADMIN_ID = "admin"
ADMIN_PASSWORD = "password"

WAIT_LOG = []                   # For ML retraining
SERVED_COUNT_FOR_RETRAIN = 0    # Retrain every 5 served users


# -------------------------------------------------------
# HELPER → FORMAT QUEUE FOR FRONTEND
# -------------------------------------------------------
def get_queue_details_for_frontend():
    detailed_queue = []

    for i, user_data in enumerate(QUEUE):
        details = user_data.copy()
        join_time_obj = details.get('timestamp')

        # Position
        position = i + 1

        # ML prediction
        predicted_wait_minutes = predict_wait_time(position)
        details['wait_time'] = round(predicted_wait_minutes, 1)

        # Join time & serve by
        if join_time_obj:
            details['join_time'] = join_time_obj.isoformat()

            serve_by_time_obj = join_time_obj + timedelta(minutes=predicted_wait_minutes)
            details['serve_by'] = serve_by_time_obj.astimezone(
                timezone(timedelta(hours=5, minutes=30))
            ).strftime('%I:%M %p')
        else:
            details['join_time'] = None
            details['serve_by'] = '--'

        # Remove raw timestamp
        if 'timestamp' in details:
            del details['timestamp']

        detailed_queue.append(details)

    return detailed_queue


# -------------------------------------------------------
# HTTP ROUTES
# -------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


# -------------------------------------------------------
# SOCKET.IO EVENTS
# -------------------------------------------------------
@socketio.on('connect')
def handle_connect():
    logging.info("✅ Client connected.")
    emit('queue_data', {'queue': get_queue_details_for_frontend()})
    emit('now_serving', {'user_id': NOW_SERVING})


@socketio.on('disconnect')
def handle_disconnect():
    logging.info("❌ Client disconnected")


@socketio.on('join_queue')
def handle_join_queue(data):
    user_id = data.get('user_id')
    user_email = data.get('email')

    logging.info(f"👋 Join request received: {user_id}")

    join_time_obj = datetime.now(timezone.utc)

    new_user = {
        'user_id': user_id,
        'user_name': user_id,
        'email': user_email,
        'timestamp': join_time_obj
    }

    QUEUE.append(new_user)
    position = len(QUEUE)

    estimated_wait = predict_wait_time(position)

    # email confirmation
    if user_email:
        serve_by_time_obj = join_time_obj + timedelta(minutes=estimated_wait)
        serve_by_time_str = serve_by_time_obj.astimezone(
            timezone(timedelta(hours=5, minutes=30))
        ).strftime('%I:%M %p')

        subject = "Queue Confirmation"
        body = (
            f"Hi {user_id},\n\n"
            f"You joined the queue.\n\n"
            f"Your position: {position}\n"
            f"Estimated wait: {estimated_wait:.1f} minutes\n"
            f"Expected serve time: {serve_by_time_str} IST"
        )

        send_email(user_email, subject, body)

    emit('position_updated', {
        'user_id': user_id,
        'position': position,
        'estimated_wait': estimated_wait
    })

    socketio.emit('queue_data', {'queue': get_queue_details_for_frontend()})


@socketio.on('next_user')
def handle_next_user():
    global NOW_SERVING, SERVED_COUNT_FOR_RETRAIN

    if QUEUE:
        served_user = QUEUE.pop(0)
        NOW_SERVING = served_user['user_name']

        logging.info(f"🔔 Now serving: {NOW_SERVING}")

        # calculate real wait time
        time_joined = served_user['timestamp']
        real_wait = (datetime.now(timezone.utc) - time_joined).total_seconds()
        WAIT_LOG.append({"duration": real_wait})

        SERVED_COUNT_FOR_RETRAIN += 1

        # retrain after 5 users
        if SERVED_COUNT_FOR_RETRAIN >= 5:
            refresh_wait_model(WAIT_LOG)
            SERVED_COUNT_FOR_RETRAIN = 0

        # notify user at position 3
        if len(QUEUE) >= 3:
            next_user = QUEUE[2]  # index 2 → position 3
            if next_user["email"]:
                est_wait = predict_wait_time(3)
                serve_by = (
                    datetime.now(timezone.utc) + timedelta(minutes=est_wait)
                ).astimezone(timezone(timedelta(hours=5, minutes=30))).strftime('%I:%M %p')

                send_email(
                    next_user["email"],
                    "You're now 3rd in Queue!",
                    f"Hi {next_user['user_name']},\n\n"
                    f"You are now 3rd.\n"
                    f"Estimated wait: {est_wait:.1f} min\n"
                    f"Expected serve: {serve_by} IST"
                )

    else:
        NOW_SERVING = None
        logging.info("Queue empty.")

    socketio.emit('now_serving', {'user_id': NOW_SERVING})
    socketio.emit('queue_data', {'queue': get_queue_details_for_frontend()})


@socketio.on('clear_queue')
def handle_clear_queue():
    global QUEUE, NOW_SERVING
    QUEUE = []
    NOW_SERVING = None

    logging.info("🗑 Queue cleared.")
    socketio.emit('now_serving', {'user_id': NOW_SERVING})
    socketio.emit('queue_data', {'queue': get_queue_details_for_frontend()})


@socketio.on('admin_login')
def handle_admin_login(data):
    if data.get('user_id') == ADMIN_ID and data.get('password') == ADMIN_PASSWORD:
        emit('login_success')
    else:
        emit('login_failed')


@socketio.on('get_queue')
def handle_get_queue():
    emit('queue_data', {'queue': get_queue_details_for_frontend()})


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
if __name__ == '__main__':
    initialize_wait_model()
    logging.info("🚀 Starting SmartQueue Server (Render-safe)...")
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
