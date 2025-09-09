import contextvars
import logging
import os
from logging.handlers import TimedRotatingFileHandler
import yaml

# 全局变量
request_id_context = contextvars.ContextVar('request_id', default='-')


class ContextualFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_context.get()
        return True


class LoggerConfig:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger(__name__)
        self._init_logging()

    def _load_config(self) -> dict:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _init_logging(self):
        logger_config = self.config['logger']
        log_file = logger_config['output']
        directory = os.path.dirname(log_file)
        if directory != "":
            os.makedirs(directory, exist_ok=True)

        handlers = [
            TimedRotatingFileHandler(
                log_file,
                when="D",
                interval=1,
                backupCount=logger_config['backupCount'],
                encoding='utf-8'
            ),
        ]

        _app_env = os.environ.get('SVC_ENV', 'dev').lower()
        if _app_env == 'dev':
            handlers.append(logging.StreamHandler())

        logger_format = "%(asctime)s - %(levelname)s - [RequestID: %(request_id)s] - %(message)s"
        for handler in handlers:
            handler.setFormatter(logging.Formatter(logger_format))
            handler.addFilter(ContextualFilter())
            self.logger.addHandler(handler)

        self.logger.setLevel(logger_config['level'].upper())
        self.logger.propagate = False

    def get_logger(self):
        return self.logger


class UvicornLoggerConfig:
    @classmethod
    def get_config(cls):
        logger_format = "%(asctime)s - %(levelname)s - [RequestID: %(request_id)s] - %(message)s"
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": logger_format,
                },
            },
            "filters": {
                "custom_filter": {
                    "()": ContextualFilter,
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "filters": ["custom_filter"],  # 添加filter到handler
                },
            },
            "root": {
                "handlers": ["default"],
                "level": "INFO",  # 统一设置为INFO级别
            },
            "loggers": {
                "uvicorn": {
                    "propagate": True,
                },
                "uvicorn.error": {
                    "propagate": True,
                },
                "uvicorn.access": {
                    "propagate": True,
                },
            },
        }


def init_logger():
    _env = os.environ.get('SVC_ENV', 'dev').lower()
    config_path = os.path.join(os.path.dirname(__file__), f'../config/{_env}.yaml')
    logger_config = LoggerConfig(config_path)
    return logger_config.get_logger()


logger = init_logger()
UVICORN_LOGGING_CONFIG = UvicornLoggerConfig.get_config()
