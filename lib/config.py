import json
import pathlib 
from typing import Self, Dict 


class Config(dict):
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        if (type(self.get(key)) is dict):
            return Config(self.get(key))
        else:
            return self.get(attr)

    def __getattr__(self, attr):
        if (type(self.get(attr)) is dict):
            return Config(self.get(attr))
        else:
            return self.get(attr)

    def copy(self) -> Self:
        return Config(dict(self))

    @classmethod
    def from_json(cls, config_file: str) -> Self:
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
