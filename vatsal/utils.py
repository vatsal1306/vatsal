import gzip
import inspect
import json
import os
import pickle
import sys
import threading
from typing import Union


class Path(str):
    """ Class for path and file related operations. Use Path('/valid/path/') for path validation."""

    def __new__(cls, val: str):
        """
        Returns path string if input path is valid. FileNotFoundError if not a valid path. TypeError otherwise.

        :param val: Absolute path to a file.
        """
        if not isinstance(val, str):
            raise TypeError(f"Expected str, got {type(val).__name__}")
        if not os.path.exists(val):
            raise FileNotFoundError(f"Path {val} does not exist.")
        return super().__new__(cls, val)

    @staticmethod
    def get_parent_dir(file_path: str) -> str:
        return "\\".join(file_path.split("\\")[:-1])

    @staticmethod
    def create_dir_if_not_exists(dir_path: str):
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except OSError as e:
                raise OSError(f"Failed to create directory {dir_path}: {e}")

    @staticmethod
    def create_file_if_not_exists(file_path: str):
        if not os.path.exists(file_path):
            try:
                open(file_path, "w").close()
            except OSError as e:
                raise OSError(f"Failed to create file {file_path}: {e}")

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
                f"Path {file_path} does not exist. If you are passing a relative path, please pass the absolute path.")

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
                f"Path {file_path} does not exist. If you are passing a relative path, please pass the absolute path.")

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


class Wrappers:
    @staticmethod
    def private_method(func):
        """ Wrap this to make a class method as a private method, i.e. can only be called internally by class,
        not from outside class or by class object."""

        def wrapper(*args, **kwargs):
            frame = inspect.currentframe().f_back
            if frame.f_locals.get('self') is None and func.__name__.startswith('_'):
                raise ValueError("Access to private method is restricted.")
            return func(*args, **kwargs)

        return wrapper

    @staticmethod
    def singleton(cls):
        """ Wrap this on a class to make it a singleton class, i.e. only one instance of that class will be created. """
        instances = dict()

        def wrap(*args, **kwargs):
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
            return instances[cls]

        return wrap


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
