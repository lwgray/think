"""
Think Jupyter Extension

This module provides Jupyter notebook integration for the Think programming language.
It includes magic commands for executing Think code and formatted error display.
"""

from IPython.core.magic import (Magics, magics_class, line_cell_magic)
from IPython.display import display, HTML
import sys
import io
from typing import Optional, Dict, Any
import argparse

from .parser import parse_think
from .interpreter import ThinkInterpreter
from .errors import ThinkError, ThinkParserError, ThinkRuntimeError

@magics_class
class ThinkMagics(Magics):
    """
    Jupyter magic commands for the Think programming language.
    
    Provides cell and line magics for executing Think code within Jupyter notebooks,
    with support for explanation mode and different formatting styles.
    """

    def __init__(self, shell):
        """Initialize Think magic with default settings."""
        super().__init__(shell)
        self.explain_mode = False
        self.style = "default"
        self.max_iterations = 5

    def parse_magic_args(self, line: str) -> argparse.Namespace:
        """
        Parse magic command arguments.

        Args:
            line: Command line arguments as a string

        Returns:
            Namespace containing parsed arguments with defaults if parsing fails
        """
        parser = argparse.ArgumentParser(description='Think magic arguments')
        parser.add_argument('--explain', action='store_true',
                          help='Enable explanation mode')
        parser.add_argument('--style', type=str, default='default',
                          choices=['default', 'minimal', 'detailed', 'color', 
                                 'markdown', 'educational'],
                          help='Set the explanation style')
        parser.add_argument('--max-iterations', type=int, default=5,
                          help='Maximum number of iterations to show in detail')

        try:
            if line:
                args = line.split()
            else:
                args = []
            return parser.parse_args(args)
        except SystemExit:
            return argparse.Namespace(explain=False, style='default', 
                                   max_iterations=5)

    def get_css_styles(self) -> str:
        """Return CSS styles for error formatting with Jupyter-specific overrides."""
        return """
        <style>
            /* Reset Jupyter's default styles that might interfere */
            .jp-OutputArea-output div {
                margin: 0;
                padding: 0;
                line-height: inherit;
            }
            
            /* Main error container with !important to override Jupyter styles */
            .think-error {
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace !important;
                white-space: pre !important;
                background-color: #1e1e1e !important;
                color: #d4d4d4 !important;
                padding: 6px !important;
                border-left: 4px solid #f14c4c !important;
                border-radius: 4px !important;
                margin: 4px 0 !important;
                line-height: 1.2 !important;
                font-size: 13px !important;
                display: block !important;
            }

            .error-content {
                padding: 2px !important;
                margin: 0 !important;
            }

            .error-title {
                color: #f14c4c !important;
                font-weight: bold !important;
                margin: 0 0 2px 0 !important;
                padding-bottom: 2px !important;
                border-bottom: 1px solid #333 !important;
                display: block !important;
            }

            .error-details {
                color: #d4d4d4 !important;
                margin: 2px 0 !important;
                line-height: 1.2 !important;
                display: block !important;
            }

            .error-details div {
                margin: 1px 0 !important;
                padding: 0 !important;
                line-height: 1.2 !important;
            }

            .source-code {
                margin: 3px 0 !important;
                padding: 2px !important;
                background-color: #2d2d2d !important;
                border-radius: 2px !important;
                display: block !important;
            }

            .code-line {
                margin: 0 !important;
                padding: 1px 0 !important;
                color: #d4d4d4 !important;
                display: block !important;
                line-height: 1.2 !important;
            }

            .error-line {
                background-color: rgba(241, 76, 76, 0.2) !important;
                color: #f14c4c !important;
            }

            .arrow {
                color: #f14c4c !important;
                margin-right: 2px !important;
                font-weight: bold !important;
                display: inline-block !important;
            }

            .line-number {
                color: #858585 !important;
                margin-right: 4px !important;
                user-select: none !important;
                display: inline-block !important;
                min-width: 1.5em !important;
                text-align: right !important;
            }

            /* Force block display for container elements */
            .variable-section {
                display: block !important;
                margin-top: 2px !important;
                padding: 2px !important;
                background-color: #2d2d2d !important;
                border-radius: 2px !important;
            }

            .variable-line {
                display: block !important;
                color: #9cdcfe !important;
                margin: 1px 0 !important;
                line-height: 1.2 !important;
            }

            .variable-value {
                color: #ce9178 !important;
            }

            .section-title {
                color: #569cd6 !important;
                margin-bottom: 1px !important;
                font-weight: bold !important;
                font-size: 12px !important;
                display: block !important;
            }
        </style>
        """

    def format_error_message(self, error: Any) -> str:
        """
        Format error messages for display in Jupyter notebooks.

        Handles both ThinkParserError and ThinkRuntimeError with appropriate
        formatting for each type.

        Args:
            error: The error object to format

        Returns:
            Formatted HTML string containing the error message and context
        """
        error_html = f"""{self.get_css_styles()}
        <div class="think-error">
            <div class="error-content">
                <div class="error-title">Think Error: {error.message}</div>"""

        if isinstance(error, ThinkParserError):
            error_html += self._format_parser_error(error)
        elif isinstance(error, ThinkRuntimeError):
            error_html += self._format_runtime_error(error)
        else:
            error_html += f"""
                <div class="error-details">
                    {str(error)}
                </div>"""

        error_html += """
            </div>
        </div>"""
        
        return error_html

    def _format_parser_error(self, error: ThinkParserError) -> str:
        """Format parser-specific error information."""
        result = f"""
            <div class="error-details">
                <div>Line: {error.line if error.line else 'Unknown'}</div>
                <div>Column: {error.column if error.column else 'Unknown'}</div>
                {f"<div>Token: '{error.token}'</div>" if error.token else ''}
            </div>"""
        
        if hasattr(error, 'source_snippet') and error.source_snippet:
            result += """
            <div class="source-code">
                <div class="section-title">Source code:</div>"""
            
            lines = error.source_snippet.split('\n')
            for line in lines:
                if '->' in line:
                    number = line.split(':')[0].strip().replace('->', '')
                    code = line.split(':')[1] if ':' in line else ''
                    result += f"""
                <div class="code-line error-line">
                    <span class="arrow">→</span><span class="line-number">{number}</span>{code.strip()}
                </div>"""
                else:
                    if ':' in line:
                        number, code = line.split(':', 1)
                        result += f"""
                <div class="code-line">
                    <span class="line-number">{number.strip()}</span>{code.strip()}
                </div>"""
            result += """
            </div>"""
        return result

    def _format_runtime_error(self, error: ThinkRuntimeError) -> str:
        """Format runtime-specific error information."""
        result = """
            <div class="error-details">"""
        
        if error.task:
            result += f"""
                <div>Task: {error.task}</div>"""
        
        if error.step:
            result += f"""
                <div>Step: {error.step}</div>"""
        
        result += """
            </div>"""
        
        if error.variables:
            result += """
            <div class="variable-section">
                <div class="section-title">Current State:</div>"""
            
            for var_name, var_value in error.variables.items():
                if isinstance(var_value, (list, dict, set)):
                    formatted_value = repr(var_value)
                elif isinstance(var_value, str):
                    formatted_value = f"'{var_value}'"
                else:
                    formatted_value = str(var_value)
                
                result += f"""
                <div class="variable-line">
                    <span class="variable-name">{var_name}</span> = <span class="variable-value">{formatted_value}</span>
                </div>"""
            
            result += """
            </div>"""
        
        return result

    @line_cell_magic
    def think(self, line: str = '', cell: Optional[str] = None) -> None:
        """
        Execute Think code in a Jupyter notebook cell.
        
        Args:
            line: Magic arguments (--explain, --style, --max-iterations)
            cell: Think code to execute
        
        Usage:
            %%think [--explain] [--style STYLE] [--max-iterations N]
            
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
            ast = parse_think(cell)
            if ast is None:
                display(HTML(self.format_error_message(
                    ThinkParserError(
                        message="Failed to parse Think code",
                        line=1,
                        column=1,
                        token="",
                        source_snippet=cell
                    )
                )))
                return
            
            interpreter = ThinkInterpreter(
                explain_mode=self.explain_mode,
                format_style=self.style,
                max_iterations_shown=self.max_iterations,
                source_code=cell
            )
            interpreter.execute(ast)
        except Exception as e:
            if isinstance(e, (ThinkParserError, ThinkRuntimeError)):
                error_html = self.format_error_message(e)
            else:
                error_html = self.format_error_message(
                    ThinkRuntimeError(
                        message=str(e),
                        task=getattr(interpreter, 'current_task', None),
                        step=getattr(interpreter, 'current_step', None),
                        variables=getattr(interpreter, 'state', {})
                    )
                )
            display(HTML(error_html))

def load_ipython_extension(ipython) -> None:
    """Register the Think magic when the extension is loaded."""
    ipython.register_magics(ThinkMagics)