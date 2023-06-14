
from tdd_paradigm.wizards_api import sort_wizards, NEEDED_WIZARDS_COUNT, wizards_factory, Wizard, Elixir, get_wizards


def test_wizard_api():
    url = "https://wizard-world-api.herokuapp.com/Wizards"
    # убираем фикстуру в функцию и реализуем получение ответа АПИ
    wizards_list = get_wizards(url)
    # Добавляем шаг преобразования в сущности из json
    wizard_entities = wizards_factory(wizards_list)
    assert all(filter(lambda x: type(x) == Wizard, wizard_entities))
    sorted_wizards_list = sort_wizards(wizard_entities)
    assert len(sorted_wizards_list) == NEEDED_WIZARDS_COUNT
    assert all(
        filter(
            lambda wizard: len(wizard.elixirs) <= len(sorted_wizards_list[0].elixirs),
            sorted_wizards_list
        )
    )

