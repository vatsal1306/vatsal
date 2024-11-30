import gzip
import json
import os
import pickle
import sys
import threading
from typing import Union


class File:
    """ Class for path and file related operations. """

    @staticmethod
    def read(file_path: str, mode: str = 'r', encoding: str = 'utf-8') -> Union[str, bytes]:
        """
        Reads the content of file. Returns a string or bytes.

        :param file_path: Absolute path to file.
        :param mode: Mode to open the file. Defaults to 'r'.
        :param encoding: Encoding mode. Defaults to 'utf-8'.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"File {file_path} does not exist. If you are passing a relative path, please pass the absolute path.")

        file_dir, file_name = os.path.split(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()

        if file_ext in ['.gz', '.gzip']:
            with gzip.open(file_path, mode, encoding=encoding) as file:
                return file.read()
        elif file_ext == '.json':
            with open(file_path, mode, encoding=encoding) as file:
                return json.load(file)
        elif file_ext == '.pickle':
            with open(file_path, mode, encoding=encoding) as file:
                return pickle.load(file)
        else:
            with open(file_path, mode, encoding=encoding) as file:
                return file.read()

    @staticmethod
    def write(file_path: str, data: Union[str, bytes], mode: str = 'w', encoding: str = 'utf-8'):
        """
        Writes the content of file. Returns a string or bytes.

        :param file_path: Absolute path to file.
        :param data: Data to write to the file.
        :param mode: Mode to open the file. Defaults to 'w'.
        :param encoding: Encoding mode. Defaults to 'utf-8'.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"File {file_path} does not exist. If you are passing a relative path, please pass the absolute path.")

        file_dir, file_name = os.path.split(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()

        if file_ext in ['.gz', '.gzip']:
            with gzip.open(file_path, mode, encoding=encoding) as file:
                file.write(data)
        elif file_ext == '.json':
            with open(file_path, mode, encoding=encoding) as file:
                json.dump(data, file)
        elif file_ext == '.pickle':
            with open(file_path, mode, encoding=encoding) as file:
                pickle.dump(data, file)
        else:
            with open(file_path, mode, encoding=encoding) as file:
                file.write(data)

    def append(self, file_path, data: Union[str, bytes], encoding: str = 'utf-8'):
        self.write(file_path, data, mode='a', encoding=encoding)

    def __str__(self):
        return "Class for path and file related operations."

    def __repr__(self):
        return "Class for path and file related operations."


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
