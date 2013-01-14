import time
from multiprocessing import Process, Queue, Event

from urx import urrtmon


class Tracker(Process):
    def __init__(self, robot_host):
        self.host = robot_host
        self._queue = Queue()
        Process.__init__(self, args=(self._queue,))
        self._stop = Event()
        self._finished = Event()
        self._data = []

    def _log(self, *args):
        print(self.__class__.__name__, ": ".join([str(i) for i in args]))

    def run(self):
        self._log("Running")
        rtmon = urrtmon.URRTMonitor(self.host)
        rtmon.start()
        while not self._stop.is_set():
            data = rtmon.get_all_data(wait=True)
            self._data.append(data)
        self._queue.put(data)
        self._finished.set()
        self._log("Closing")

    def start_acquisition(self):
        self.start()

    def stop_acquisition(self):
        self._stop.set()

    def get_result(self):
        self._stop.set()
        while not self._finished.is_set():
            time.sleep(0.01)
        return self._queue.get()

    def shutdown(self, join=True):
        self._stop.set() # just to make sure 
        self._log("Shutting down")
        if join:
            self.join()


if __name__ == "__main__":
    p = Tracker()
    try:
        p.start_acquisition()
        time.sleep(3)
        p.stop_acquisition()
        a = p.get_result()
        print("Result is: ", a)
    finally:
        p.shutdown()


