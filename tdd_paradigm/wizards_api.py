import dataclasses
from typing import List

import requests as requests

NEEDED_WIZARDS_COUNT = 5


@dataclasses.dataclass
class Elixir:
    id: str = ""
    name: str = ""


@dataclasses.dataclass
class Wizard:
    id: str = ""
    elixirs: List[Elixir] = list
    first_name: str = ""
    last_name: str = ""


def get_wizards(url):
    response = requests.get(url)
    return response.json()


def wizards_factory(wizards_json: List[dict]) -> List[Wizard]:
    return [
        Wizard(
            first_name=wizard.get("firstName"),
            last_name=wizard.get("lastName"),
            id=wizard.get("id"),
            elixirs=[
                Elixir(
                    id=elixir.get("id"),
                    name=elixir.get("name")
                ) for elixir in wizard.get("elixirs")
            ],
        ) for wizard in wizards_json
    ]


def sort_wizards(wizards: List[Wizard]) -> List[Wizard]:
    return sorted(wizards, key=lambda wizard: len(wizard.elixirs))[:NEEDED_WIZARDS_COUNT]
