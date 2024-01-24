
import threading

class MyThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._terminate = threading.Event()

    def terminate(self):
        self._terminate.set()
        print("Terminated thread")