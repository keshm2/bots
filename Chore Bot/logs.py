import logging
from datetime import datetime
import os

class Logger:
    def __init__(self, name: str, log_file: str = 'logs.log'):
        script_path = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(script_path, "logs.log")
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            fh = logging.FileHandler(filename=log_path, encoding='utf-8', mode='a+')
            fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

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
    
    