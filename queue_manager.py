class QueueManager:
    def __init__(self):
        self.queue = []
        self.counter = 1

    def add_user(self, user, email):
        entry = {
            "id": self.counter,
            "user": user,
            "email": email
        }
        self.queue.append(entry)
        self.counter += 1
        return entry["id"]

    def pop_user(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def get_queue(self):
        return self.queue

    def queue_size(self):
        return len(self.queue)

    def clear(self):
        self.queue = []
        self.counter = 1
