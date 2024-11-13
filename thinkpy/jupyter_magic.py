from IPython.core.magic import (Magics, magics_class, line_cell_magic)
from IPython.display import display, HTML
import sys
import io
from typing import Optional

from .parser import parse_thinkpy
from .interpreter import ThinkPyInterpreter

@magics_class
class ThinkPyMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self.explain_mode = False

    @line_cell_magic
    def thinkpy(self, line='', cell=None):
        """
        Execute ThinkPy code in a Jupyter notebook cell.
        Usage: %%thinkpy [--explain]
        """
        # If used as line magic and cell is empty
        if cell is None:
            cell = line
            line = ''

        # Parse options
        self.explain_mode = '--explain' in line
        
        # Capture output
        old_stdout = sys.stdout
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        
        try:
            # Parse the code
            ast = parse_thinkpy(cell)
            if ast is None:
                display(HTML('<div style="color: red;">Error: Failed to parse ThinkPy code</div>'))
                return
            
            # Create and run interpreter
            interpreter = ThinkPyInterpreter(explain_mode=self.explain_mode)
            interpreter.execute(ast)
            
            # Get output and state
            output = output_buffer.getvalue()
            final_state = interpreter.state
            
            # Display results
            if output:
                display(HTML(f'<div style="font-family: monospace;">Program output:<br>{output}</div>'))
            
            if self.explain_mode:
                display(HTML(
                    '<div style="background-color: #f0f0f0; padding: 10px; margin: 10px 0;">'
                    '<b>Final Program State:</b><br>'
                    f'<pre>{str(final_state)}</pre>'
                    '</div>'
                ))
                
        except Exception as e:
            display(HTML(f'<div style="color: red;">Error executing ThinkPy code: {str(e)}</div>'))
        
        finally:
            sys.stdout = old_stdout

def load_ipython_extension(ipython):
    """
    Register the ThinkPy magic when the extension is loaded.
    """
    ipython.register_magics(ThinkPyMagics)