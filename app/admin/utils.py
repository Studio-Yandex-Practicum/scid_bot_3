def extract_fields(objects, *fields):
    """Извлекает указанные поля из списка объектов."""
    return [[getattr(obj, field) for field in fields] for obj in objects]
