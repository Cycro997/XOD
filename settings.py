import os
import json
from types import GenericAlias as alias

path = os.path.dirname(os.path.realpath(__file__))

def get_raw_settings():
    with open(f"{path}/config.json") as file:
        return file.read()

def get_settings():
    return json.loads(get_raw_settings())

def set_raw_settings(new_settings: str):
    with open(f"{path}/config.json", "w") as file:
        file.write(new_settings)

def set_settings(new_settings):
    set_raw_settings(json.dumps(new_settings, indent=4))

def to_path(path_: str):
    split = path_.split("/")
    split = [
        (
            int(i) if i.startswith("#") and i.isnumeric()
            else i
        ) for i in split  
    ]
    return path_.split("/")

def get_setting(setting: str):
    spath = to_path(setting) # Setting path
    item = get_settings()
    for i in spath:
        try:
            item = item[i]
        except (KeyError, IndexError):
            raise ValueError(f"Setting {setting} does not exist")
    return item

def set_setting(setting: str, new_value):
    spath = to_path(setting) # Setting path
    settings = get_settings()
    item = settings
    for i in spath[:-1]:
        try:
            item = item[i]
        except (KeyError, IndexError):
            raise ValueError(f"Setting {setting} does not exist")
    try:
        item[spath[-1]] = new_value
    except (KeyError, IndexError):
        raise ValueError(f"Setting {setting} does not exist")
    set_settings(settings)

def del_setting(setting: str):
    spath = to_path(setting) # Setting path
    settings = get_settings()
    item = settings
    for i in spath[:-1]:
        try:
            item = item[i]
        except (KeyError, IndexError):
            raise ValueError(f"Setting {setting} does not exist")
    try:
        del item[spath[-1]]
    except (KeyError, IndexError):
        raise KeyError(f"Setting {setting} does not exist")
    set_settings(settings)
