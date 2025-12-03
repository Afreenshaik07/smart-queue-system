# queue_manager.py - FINAL FULL VERSION

class QueueManager:
    def __init__(self):
        self.queue = []
        self.current_number = 0

    def add_user(self, name):
        """Add a user to the queue and return their assigned number."""
        self.current_number += 1
        user = {"id": self.current_number, "name": name}
        self.queue.append(user)
        return user["id"]

    def get_position(self, user_id):
        """Return the position of the user in the queue."""
        for index, user in enumerate(self.queue):
            if user["id"] == user_id:
                return index + 1
        return None

    def get_next(self):
        """Serve the next user."""
        if self.queue:
            return self.queue.pop(0)
        return None

    def total_waiting(self):
        """Return how many are in the queue."""
        return len(self.queue)
