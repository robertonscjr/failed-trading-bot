import logging
import os


class Log:
    def __init__(self, name, output_file_path):
        self._verify_existing_paths()
        self.logger = logging.getLogger(name)
        if not len(self.logger.handlers):
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            self.logger.addHandler(handler)
            handler = logging.FileHandler(output_file_path)
            self.logger.addHandler(handler)

    def log(self, text):
        self.logger.info(text)

    def _verify_existing_paths(self):
        if not os.path.exists('logs'):
            os.mkdir('logs')

def configure_logging():
    logging.basicConfig(level=logging.INFO)
