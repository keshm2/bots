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

import json, os

def update_ids(file_path: str = None) -> bool:
    if file_path is None:
        return False

    abs_path = os.path.abspath(file_path)
    print(f"Updating file: {abs_path}")

    with open(abs_path, "r") as file:
        data = json.load(file)

    print("Before:", data)

    data["list_id"] = data.get("list_id", 0) + 1

    print("After:", data)

    with open(abs_path, "w") as file:
        json.dump(data, file, indent=4)

    # Re-read immediately to verify
    with open(abs_path, "r") as file:
        check = file.read()
        print("File now contains:\n", check)

    return True
