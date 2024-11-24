import pytest
from thinkpy.parser import ThinkPyParser
from thinkpy.interpreter import ThinkPyInterpreter

@pytest.fixture
def parser():
    return ThinkPyParser()

@pytest.fixture
def interpreter():
    return ThinkPyInterpreter(explain_mode=False)
