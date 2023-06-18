import requests
from src.errors import EnvironmentException, UnauthorizedException


def test_environment_exception():
    try:
        raise EnvironmentException("test")
    except EnvironmentException as e:
        assert e.message == "test"
        assert e.name == "EnvironmentException"
        assert str(e) == "EnvironmentException: test"


def test_unauthorized_exception():
    try:
        raise UnauthorizedException("test")
    except UnauthorizedException as e:
        assert e.message == "test"
        assert e.name == "UnauthorizedException"
        assert str(e) == "UnauthorizedException: test"
