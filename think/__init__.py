"""
Think - A language for learning computational thinking
"""

from .parser import parse_think
from .interpreter import ThinkInterpreter
from . import jupyter_magic

__version__ = "0.1.9"
__all__ = ["parse_think", "ThinkInterpreter", "jupyter_magic"]
