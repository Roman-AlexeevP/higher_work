def get_disallowed_defects(
    defects: List[DefectParams], grades: List[GradeParams]
) -> dict:
    disallowed_defects_by_grades = {grade.name: set() for grade in grades}
    for defect in defects:
        for rule in defect.rules:
            if rule.size == 0:
                disallowed_defects_by_grades[rule.grade].append(defect.label)

    return disallowed_defects_by_grades


def test_foo_bar():

    # some code
    assert defect.label not in disallowed_defects[piece.grade.name]
    # .... more some code