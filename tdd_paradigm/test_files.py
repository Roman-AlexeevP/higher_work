import json
from pathlib import Path

import pytest

from tdd_paradigm.files import manage_files, Action


@pytest.fixture
def temp_files(tmp_path):
    files = []
    for i in range(10):
        file_path = tmp_path / Path(f"test_{i}.json")
        file_path.touch(exist_ok=True)
        files.append(file_path)
    return tmp_path, files

def test_files_list(temp_files):
    tmp_dir, files = temp_files
    result = manage_files(directory=tmp_dir)

    assert sorted(result) == ([file.name for file in files])

def test_create_file(temp_files):
    tmp_dir, files = temp_files
    test_content = {"test": "test"}
    test_filename = "new_file.json"
    manage_files(directory=tmp_dir, action=Action.CREATE, content=test_content, filename=test_filename)
    assert test_filename in [file.name for file in tmp_dir.iterdir()]
    new_test_content = {"test": "new_test"}
    manage_files(directory=tmp_dir, action=Action.CREATE, content=new_test_content, filename=test_filename)
    new_file = tmp_dir / test_filename
    with open(new_file, "r") as f:
        content = json.loads(f.read())
        assert content == new_test_content

    with pytest.raises(ValueError):
        manage_files(directory=tmp_dir, action=Action.CREATE, content=None, filename=test_filename)

def test_delete_file(temp_files):
    tmp_dir, files = temp_files
    file_to_delete = files[0]
    manage_files(directory=tmp_dir, action=Action.DELETE, filename=file_to_delete)

    assert file_to_delete not in [file.name for file in tmp_dir.iterdir()]
    with pytest.raises(ValueError):
        manage_files(directory=tmp_dir, action=Action.DELETE, filename="non_existsing.png")