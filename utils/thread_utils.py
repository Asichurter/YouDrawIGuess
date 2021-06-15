from threading import Lock


class ThreadValue:
    def __init__(self, val):
        self._val = val
        self._lock = Lock()

    def get_val(self):
        self._lock.acquire()
        val = self._val
        self._lock.release()
        return val

    def write_val(self, val):
        self._lock.acquire()
        self._val = val
        self._lock.release()