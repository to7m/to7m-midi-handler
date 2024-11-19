from time import sleep
from queue import Queue, Empty
import pyudev


FIRST_EVENT_DELAY = 0.06
RECHECK_DELAY = 0.01


class _UsbWatcher(pyudev.MonitorObserver):
    def __init__(self, queue):
        self.queue = queue

        udev_monitor = pyudev.Monitor.from_netlink(pyudev.Context())
        udev_monitor.filter_by("usb", device_type="usb_device")
        self._udev_observer = pyudev.MonitorObserver(
            udev_monitor, callback=self._add_udev_event_to_queue
        )

    def _add_udev_event_to_queue(self, device):
        self._queue.put("udev event detected")

    def start(self):
        self._udev_observer.start()

    def stop(self):
        self._udev_observer.stop()


class Watcher:
    def __init__(self):
        self.queue = Queue()
        self._usb_watcher = _UsbWatcher(self.queue)

    def __enter__(self):
        self._usb_watcher.start()
        return self

    def __exit__(self, err_type, err_value, traceback):
        self._usb_watcher.stop()

    def _flush_remaining_events(self):
        events_found = False

        try:
            while True:
                self.queue.get(block=False)
                events_found = True
        except Empty:
            return events_found

    def wait_for_events(self):
        self.queue.get()
        sleep(FIRST_EVENT_DELAY)

        while True:
            events_found = self._flush_remaining_events()
            if events_found:
                sleep(RECHECK_DELAY)
            else:
                return
