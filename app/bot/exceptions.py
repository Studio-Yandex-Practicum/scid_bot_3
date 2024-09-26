class RequestExceptionError(Exception):
    """Ошибка запроса."""
    pass


class EmptyResponseError(Exception):
    """В запросе нет необходимых ключей."""
    pass


class ResponceTypeError(TypeError):
    """Неверный тип ответа."""
    pass


class UndocumentedStatusError(Exception):
    """Недокументированный статус."""
    pass
