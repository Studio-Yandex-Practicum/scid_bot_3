from app.helpers import is_valid_name, is_valid_phone_number


def test_is_valid_name():
    assert is_valid_name("John")
    assert is_valid_name("Анна")
    assert not is_valid_name("123")


def test_is_valid_phone_number():
    assert is_valid_phone_number("+71234567890")
    assert is_valid_phone_number("81234567890")
    assert not is_valid_phone_number("12345")
