from IPython.core.magic import (Magics, magics_class, line_cell_magic)
from IPython.display import display, HTML
import sys
import io
from typing import Optional
import argparse

from .parser import parse_thinkpy
from .interpreter import ThinkPyInterpreter

@magics_class
class ThinkPyMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self.explain_mode = False
        self.style = "default"
        self.max_iterations = 5

    def parse_magic_args(self, line):
        """Parse magic arguments using argparse"""
        parser = argparse.ArgumentParser(description='ThinkPy magic arguments')
        parser.add_argument('--explain', action='store_true',
                          help='Enable explanation mode')
        parser.add_argument('--style', type=str, default='default',
                          choices=['default', 'minimal', 'detailed', 'color', 'markdown', 'educational'],
                          help='Set the explanation style')
        parser.add_argument('--max-iterations', type=int, default=5,
                          help='Maximum number of iterations to show in detail')

        # Parse args and handle errors gracefully
        try:
            # Split the line into args and handle quotes properly
            if line:
                args = line.split()
            else:
                args = []
            parsed_args = parser.parse_args(args)
            return parsed_args
        except SystemExit:
            # Catch the system exit that argparse triggers on error
            return argparse.Namespace(explain=False, style='default', max_iterations=5)

    def format_error_message(self, error):
        """Format error message with proper styling"""
        css = """
        <style>
            .thinkpy-error {
                font-family: monospace;
                white-space: pre;
                background-color: #fff0f0;
                padding: 15px;
                border-left: 4px solid #ff0000;
            }
            .error-content {
                background-color: #ffffff;
                padding: 15px;
                border-radius: 3px;
            }
            .error-title {
                color: #ff0000;
                margin-bottom: 15px;
            }
            .error-location {
                color: #000;
                line-height: 1;
                text-align: left;
            }
            .context-label {
                color: #000;
                line-height: 1;
                text-align: left;
            }
            .token-info {
                color: #000;
                line-height: 1;
                text-align: left;
            }
            .source-code {
                color: #000;
                line-height: 1;
                text-align: left;
            }
            .code-line {
                white-space: pre;
                line-height: 1;
                text-align: left;
            }
            .line-number {
                display: inline-block;
                width: 30px;
                color: #000;
            }
            .line-content {
                display: inline;
                color: #000;
            }
            .error-line .line-number {
                color: #ff0000;
            }
            .error-line .line-content {
                color: #ff0000;
            }
            .arrow {
                color: #ff0000;
                margin-right: 5px;
            }
        </style>
        """
        
        error_html = f""" 
        {css}
        <div class="thinkpy-error">
        <div class="error-content" style="color: black;">
        <span style="color: red;">
        ThinkPy Error: {error.message}
        </span> 
        Line: {error.line} 
        Column: {error.column} 
        Context: Near token: '{error.token}'
        </span>
        Source code:
        """    
        
        # Format source code lines
        if hasattr(error, 'source_snippet'):
            lines = error.source_snippet.split('\n')
            for line in lines:
                if '->' in line:
                    # Error line
                    number = line.split(':')[0].strip().replace('->', '')
                    code = line.split(':')[1] if ':' in line else ''
                    error_html += f"""
<p style="color: red;">--> {number}:{' ' * 8}{code.strip()}</p>"""
                else:
                    # Normal line
                    if ':' in line:
                        number, code = line.split(':', 1)
                        error_html += f"""
{number.strip()}:{' ' * 8}{code.strip()}"""
        
        error_html += """
            </div>
        </div>"""
        return error_html

    @line_cell_magic
    def thinkpy(self, line='', cell=None):
        """Execute ThinkPy code in a Jupyter notebook cell.
        
        Usage:
            %%thinkpy [--explain] [--style STYLE] [--max-iterations N]
            
        Styles:
            default    - Basic bracketed format
            minimal    - Clean, simple format
            detailed   - With separators
            color      - With ANSI colors
            markdown   - Using Markdown-style headers
            educational - With emoji icons and detailed explanations
            
        Max iterations:
            Controls how many loop iterations to show in detail
            Default is 5
        """
        if cell is None:
            cell = line
            line = ''

        # Parse magic arguments
        args = self.parse_magic_args(line)
        self.explain_mode = args.explain
        self.style = args.style
        self.max_iterations = args.max_iterations
        
        try:
            # Parse and execute the code
            ast = parse_thinkpy(cell)
            if ast is None:
                display(HTML(self.format_error_message("Failed to parse ThinkPy code")))
                return
            
            # Creatae a StringIO buffer to capture stdout
            output_buffer = io.StringIO()
            sys.stdout = output_buffer
            
            interpreter = ThinkPyInterpreter(
                explain_mode=self.explain_mode,
                format_style=self.style,
                max_iterations_shown=self.max_iterations
            )
            interpreter.execute(ast)

            # Restore stdout
            sys.stdout = sys.__stdout__
            output = output_buffer.getvalue()

            # If using color style, wrap output in proper HTML
            if self.style == 'color':
                html_output = f"""
                <div style="font-family: monospace: white-space: pre;">
                    {output}
                </div>
                """
                display(HTML(html_output))
            else:
                print(output)
            
        except Exception as e:
            sys.stdout = sys.__stdout__
            if hasattr(e, 'format_message'):
                error_html = self.format_error_message(e)
            else:
                error_html = self.format_error_message(type('ThinkPyError', (), {
                    'message': str(e),
                    'line': None,
                    'column': None,
                    'token': '',
                    'source_snippet': ''
                }))
            display(HTML(error_html))

def load_ipython_extension(ipython):
    """Register the ThinkPy magic when the extension is loaded."""
    ipython.register_magics(ThinkPyMagics)