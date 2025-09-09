# -*- coding: utf-8 -*-
import os
import yaml
from typing import Any, Dict


class ConfigLoader:
    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self, app_env: str = None):
        if not self._config:
            if app_env is None:
                app_env = os.environ.get('SVC_ENV', 'config').lower()
            self._load_config(app_env)

    def _load_config(self, app_env: str):
        cur_path = os.path.dirname(os.path.realpath(__file__))
        yaml_path = os.path.join(cur_path, f"../config/{app_env}.yaml")
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                self._config = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {yaml_path} not found.")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {yaml_path}: {e}")

    def get_config(self) -> Dict[str, Any]:
        return self._config


GLOBAL_CONFIG = ConfigLoader().get_config()
