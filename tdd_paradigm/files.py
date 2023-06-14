import json
from pathlib import Path


class Action:
    CREATE = 1
    DELETE = 2


def manage_files(directory: Path, filename: str = None, action: Action = None, content: dict = None):

    if filename is None and action is None:
        return [file.name for file in directory.iterdir()]

    mapping_actions = {
        Action.DELETE: delete_file,
        Action.CREATE: create_file
    }
    file = directory / filename
    return mapping_actions[action](file, content)

def create_file(filename: Path, content: dict):
    if filename.exists() and content is None:
        raise ValueError()
    with open(filename, "w") as f:
        json.dump(content, f)
    return filename



def delete_file(filename: Path, content: dict):
    if not filename.exists():
        raise ValueError()
    filename.unlink()