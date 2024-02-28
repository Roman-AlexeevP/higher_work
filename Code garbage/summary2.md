### 1 кейс

```python
# Сортировка + фильтрация файлов статусов. Сортировка в генераторе

sorted_statuses = sorted(
        (task for task in tasks if task.status is not None),
        key=lambda task:task.id,
        reverse=True
)


```

