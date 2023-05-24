

class DefectParams:

    # some code
    # Наше свойство для конкретного дефекта
    @property
    def allowed_grades(self):
        return {rule.grade for rule in filter(lambda rule: rule.size != 0, self.rules)}


# Итоговая проверка будет:

assert piece.grage.name in defect.allowed_grades