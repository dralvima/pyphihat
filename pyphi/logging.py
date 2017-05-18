import tqdm
import sys
import logging
import threading
import contextlib


class LockedProgressBar(tqdm.tqdm):
    """Thread safe progress-bar wrapper around ``tqdm``."""

    @property
    def _lock(self):
        return logging._handlers['stdout'].lock

#    _lock = threading.RLock()

    def __init__(self, *args, **kwargs):
        with self._lock:
            super().__init__(*args, **kwargs)

    @classmethod
    def write(cls, *args, **kwargs):
        with cls._lock:
            super().write(*args, **kwargs)

    def update(self, *args, **kwargs):
        with self._lock:
            super().update(*args, **kwargs)

    def close(self):
        with self._lock:
            super().close()


class DummyProgressBar:

    def __init__(self, *args, **kwargs):
        pass

    def write(cls, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def close(self):
        pass


def ProgressBar(disable=False, **kwargs):
    if disable:
        cls = DummyProgressBar
    else:
        cls = LockedProgressBar

    return cls(**kwargs)


class ProgressBarHandler(logging.StreamHandler):
    """Logging handler which writes through ``tqdm`` in order to not break
    progress bars.
    """
    def emit (self, record):
        try:
            msg = self.format(record)
            ProgressBar.write(msg, file=self.stream)
            self.flush()
        except Exception:
            self.handleError(record)
