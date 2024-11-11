"""
ThinkPy - A language for learning computational thinking
"""

from .parser import parse_thinkpy
from .interpreter import ThinkPyInterpreter

__version__ = "0.1.0"
__all__ = ["parse_thinkpy", "ThinkPyInterpreter"]