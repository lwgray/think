"""
ThinkPy - A language for learning computational thinking
"""

from .parser import parse_thinkpy
from .interpreter import ThinkPyInterpreter
from . import jupyter_magic

__version__ = "2.0.0"
__all__ = ["parse_thinkpy", "ThinkPyInterpreter", "jupyter_magic"]
