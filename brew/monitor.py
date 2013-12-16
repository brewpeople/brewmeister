import time
import threading
from . import app, mongo, controller
from bson.objectid import ObjectId


class Monitor(object):
    def __init__(self, timeout=10):
        self.thread = None
        self.exit_event = None
        self.timeout = timeout

    def temperature(self, brew_id):
        if self.thread:
            raise RuntimeError("Brew still ongoing")

        def run_in_background():
            while True:
                if self.exit_event.wait(self.timeout):
                    break

                with app.app_context():
                    temperature = controller.get_temperature()
                    now = time.time()
                    query = {'_id': ObjectId(brew_id)}
                    op = {'$push': {'temperatures': (now, temperature)}}

                    mongo.db.brews.update(query, op)

        self.exit_event = threading.Event()

        self.thread = threading.Thread(target=run_in_background)
        self.thread.start()

    def stop(self):
        self.exit_event.set()
        self.thread.join()
        self.thread = None
