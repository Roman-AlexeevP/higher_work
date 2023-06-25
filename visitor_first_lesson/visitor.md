# Описание паттерна

Паттерн Visitor позволяет при наличии метода accept() в ветке классов гибко их модифицировать без необходимости переписывания
 и доступа к внутренней реализации.

Этот паттерн позволяет нам держать классы закрытыми для изменений, но открытыми для расширения.

Реализуется он наличием метода accept(visitor) в интерфейсе класса и последующей реализацией классов-посетителей с методом
 visit().

# Пример использования

```python

# ветка классов-валидаторов для различных видов архивов в системе:

class ZipValidator:

    def validate(self):
        # проверяем корректный ли файл, точно ли он zip, его размер если потребуется
        if not self.zipfile.is_zipfile(zip_file):
            raise ValidationError()
        with self.zipfile.ZipFile(self.zip_file, "r") as archive:
            if archive.testzip() is not None:
                raise ValidationError()
            
# Наследуемся от главного класса для того, чтобы проверять также конкретные архивы с системными файлами или файлами XML

class XMLZipValidator(ZipValidator):

    def validate(self):
        # здесь уже придется проверять насколько схема корректна, есть ли нужные поля, и метод придется перегружать
        for file in self.FILES_TO_CHECK:
            with file.open(file, "r") as xml:
                self._validate_xml_by_schema(xml, self.SCHEMA_FILE)

# В данном случае, например, схемы проверять не надо, нужно узнать есть ли обязателньые файлы

class SystemZipValidator(ZipValidator):

    def validate(self):
        dirnames = archive.namelist()
        if not all([dirname in IMPORTANT_FILES for dirname in dirnames]):
            raise VAlidationError()
``` 

Теперь применим паттерн Visitor:


```python
class ZipValidator:
    
    def accept(self, visitor):
        visitor.visit(self)
        
    def validate(self):
        # проверяем корректный ли файл, точно ли он zip, его размер если потребуется
        if not self.zipfile.is_zipfile(zip_file):
            raise ValidationError()
        with self.zipfile.ZipFile(self.zip_file, "r") as archive:
            if archive.testzip() is not None:
                raise ValidationError()
            
        
class Visitor:

    def visit(self, entity):
        raise NotImplementedError

class ValidateXMLinZipVisitor(Visitor):

    def visit(self, entity:XMLZipValidator):
        for file in entity.FILES_TO_CHECK:
            with file.open(file, "r") as xml:
                entity._validate_xml_by_schema(xml, entity.SCHEMA_FILE)

class ValidateSystemInZipVIsitor(Visitor):

    def visit(self, entity):
        dirnames = entity.archive.namelist()
        if not all([dirname in entity.IMPORTANT_FILES for dirname in dirnames]):
            raise ValidationError()

# теперь добавлений новых проверок сводится к 
# validator = SystemZipValidator()
# visitor = ValidateSystemInZipVisitor()
# validator.accept(visitor)
```

В целом, это очень мощная абстракция, которая позволяет расширять поведение очень чистым и понятным способом, много раз я 
спотыкался об грабли расширения и вместо простого добавления нового функционала заодно придумывал как реорганизовать то, что
написал 2 месяца назад. Так буду стараться применять эту идею на практике почаще.
