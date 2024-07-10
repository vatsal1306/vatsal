import sys
import os
import threading


class ProgressPercentage:
    """
    Callback function to show progress of file upload.
    """

    def __init__(self, filename):
        """
        Initialize ProgressPercentage object.
        :param filename: Name of the file
        """
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        """
        Show progress of file upload. To simplify, assume this is hooked up to a single filename
        :param bytes_amount: Bytes uploaded
        """
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s Bytes (%.2f%%)" % (self._filename, self._seen_so_far, self._size, percentage))
            sys.stdout.flush()
