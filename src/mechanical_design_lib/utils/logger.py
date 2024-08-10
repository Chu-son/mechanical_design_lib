import os
from logging import getLogger, StreamHandler, Formatter, FileHandler, DEBUG

from mechanical_design_lib.utils.util import DirectoryFactory


class LoggerFactory:
    __LOGGERS = {}

    @classmethod
    def get_logger(cls, name: str):
        if cls.__LOGGERS.get(name) is None:

            logger = getLogger(name)
            logger.setLevel(DEBUG)

            formatter = Formatter(
                fmt='%(asctime)s %(levelname)s %(name)s :%(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # StreamHandler
            stream_handler = StreamHandler()
            stream_handler.setFormatter(formatter)
            stream_handler.setLevel(DEBUG)
            logger.addHandler(stream_handler)

            # FileHandler
            log_path = DirectoryFactory.get_directory(
                DirectoryFactory.DirectoryName.LOG)
            log_file_path = f"{log_path}/{name}.log"

            file_handler = FileHandler(log_file_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(DEBUG)
            logger.addHandler(file_handler)

            logger.info(f"Logger {name} created with log file {log_file_path}")

            # Add the logger to the dictionary
            cls.__LOGGERS[name] = logger

        return cls.__LOGGERS[name]
