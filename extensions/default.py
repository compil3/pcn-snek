import json
import pathlib

def config():
    """Fetchs config file"""
    path = pathlib.Path.cwd()
    print(path)
    for file in path.glob(f"*.json"):
        print(file)
        try:
            with open(file, encoding='utf8') as data:
                return json.load(data)
        except FileNotFoundError:
            raise FileNotFoundError("JSON file wasn't found.")