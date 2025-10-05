import logging
from datetime import datetime
import os
import json

class Logger:
    def __init__(self, name: str, log_file: str = 'logs.log'):
        script_path = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(script_path, "logs.log")
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            fh = logging.FileHandler(filename=log_path, encoding='utf-8', mode='a+')
            fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

    def debug(self, msg: str = None):
        if msg is not None:
            self.logger.debug(msg)
        else:
            pass

    def info(self, msg: str = None):
        if msg is not None:
            self.logger.info(msg)
        else:
            pass
    
    def warning(self, msg: str = None):
        if msg is not None:
            self.logger.warning(msg)
        else:
            pass
    
    def error(self, msg: str = None):
        if msg is not None:
            self.logger.error(msg)
        else:
            pass
    
    def critical(self, msg: str = None):
        if msg is not None:
            self.logger.critical(msg)
        else:
            pass
    
def load_ids(file_path: str = None, log: Logger = None) -> int:
    if file_path is not None and log is not None:
        with open(file_path, "r+") as file:
            data = json.load(file)
            return data.get("list_id", 1)
    else:
        log.warning(f"Incorrect file path provided: {file_path}, load_ids will return -1!")
        return -1

def update_ids(file_path: str = None) -> bool:
    if file_path is None:
        return False

    abs_path = os.path.abspath(file_path)

    with open(abs_path, "r") as file:
        data = json.load(file)

    data["list_id"] = data.get("list_id", 0) + 1

    with open(abs_path, "w") as file:
        json.dump(data, file, indent=4)

    return True

def load_chores(file_path: str = None):
    if file_path is not None:
        with open(file_path, 'r+') as file:
            return json.load(file)
    return {}

def save_chores(data, file_path: str = None, append: bool = False):
    if append:
        with open(file_path, "a+") as file:
            print()
    else:
        with open(file_path, "w+") as file:
            json.dump(data, file, indent=4)

