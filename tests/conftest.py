import pytest
from think.parser import ThinkParser
from think.interpreter import ThinkInterpreter

@pytest.fixture
def parser():
    return ThinkPyParser()

@pytest.fixture
def interpreter():
    return ThinkPyInterpreter(explain_mode=False)
