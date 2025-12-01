import json
import pathlib 
from collections import UserDict
from typing import Dict, Union, Any


class Config(UserDict):
    def __init__(self, *args: Dict[str, Any], **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: str) -> Union[Dict[str, Any], Any]:
        val = self.data[key]
        if (type(val) is dict):
            self.data[key] = Config(val)
            
        return self.data[key]

    def __getattr__(self, attr: str) -> Union[Dict[str, Any], Any]:
        val = self.get(attr)
        if (type(val) is dict):
            self.data[attr] = Config(val)
            
        return self.data[attr]

    def copy(self) -> Config:
        return Config(dict(self))

    @classmethod
    def from_json(cls, config_file: str) -> Config:
        try:
            with open(pathlib.Path(config_file), 'r') as file:
                config = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Config file not found at {config_file}."
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        return cls(config)
