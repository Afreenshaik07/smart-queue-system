import logging
from datetime import datetime

class QueueManager:

    def __init__(self):
        self.queue = []
        logging.info("QueueManager initialized")

    def add_user(self, user_id, email):
        position = len(self.queue) + 1

        entry = {
            "user_id": user_id,
            "user_name": user_id,
            "email": email,
            "join_time": datetime.utcnow().isoformat(),
        }

        self.queue.append(entry)
        logging.info(f"User added: {entry}")
        return position

    def pop_user(self):
        if not self.queue:
            return None
        return self.queue.pop(0)

    def get_queue(self):
        return self.queue


# IMPORTANT: EXPORT manager instance
manager = QueueManager()
