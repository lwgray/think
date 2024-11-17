"""
ThinkPy - A language for learning computational thinking
"""

from .parser import parse_thinkpy
from .interpreter import ThinkPyInterpreter
from . import jupyter_magic

__version__ = "0.1.9"
__all__ = ["parse_thinkpy", "ThinkPyInterpreter", "jupyter_magic"]
