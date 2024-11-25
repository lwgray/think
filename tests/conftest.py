import pytest
from think.parser import ThinkParser
from think.interpreter import ThinkInterpreter

@pytest.fixture
def parser():
    return ThinkParser()

@pytest.fixture
def interpreter():
    return ThinkInterpreter(explain_mode=False)
