from typing import Optional, Any
from .errors import ThinkError, ThinkParserError, ThinkRuntimeError

class ThinkValidator:
    """Validates Think programs for correctness and completeness."""
    
    def __init__(self):
        self.defined_tasks: set[str] = set()
        self.run_tasks: set[str] = set()
        self.source_code: Optional[str] = None
        
    def validate_program(self, ast: dict[str, Any], source_code: str) -> None:
        """
        Validates a Think program AST for correctness.
        
        Args:
            ast: The Abstract Syntax Tree of the Think program
            source_code: Original source code for error reporting
            
        Raises:
            ThinkParserError: If program structure is invalid
            ThinkRuntimeError: If runtime validation fails
        """
        self.source_code = source_code
        
        if not ast:
            raise ThinkParserError(
                message="Empty or invalid program",
                line=1,
                column=1,
                token="",
                source_snippet=self._get_context_lines(1)
            )
            
        # Validate tasks exist
        if 'tasks' not in ast or not ast['tasks']:
            raise ThinkParserError(
                message="Program must contain at least one task",
                line=1,
                column=1,
                token="",
                source_snippet=self._get_context_lines(1)
            )
            
        # Collect defined tasks
        self.defined_tasks = set(task['name'] for task in ast['tasks'])
            
        # Validate runs exist
        if 'runs' not in ast or not ast['runs']:
            last_task_line = self._find_last_task_line(ast['tasks'])
            raise ThinkParserError(
                message="Program must contain at least one run statement",
                line=last_task_line + 1,
                column=1,
                token="",
                source_snippet=self._get_context_lines(last_task_line)
            )
            
        # Collect run tasks
        self.run_tasks = set(ast['runs'])
        
        # Validate all tasks are run
        unrun_tasks = self.defined_tasks - self.run_tasks
        if unrun_tasks:
            raise ThinkRuntimeError(
                message=f"Tasks defined but never run: {', '.join(unrun_tasks)}",
                task="Program Validation",
                step="Run Statement Check",
                variables={
                    "defined_tasks": list(self.defined_tasks),
                    "run_tasks": list(self.run_tasks)
                }
            )
            
        # Validate all run tasks exist
        undefined_runs = self.run_tasks - self.defined_tasks
        if undefined_runs:
            raise ThinkRuntimeError(
                message=f"Attempting to run undefined tasks: {', '.join(undefined_runs)}",
                task="Program Validation",
                step="Task Definition Check",
                variables={
                    "defined_tasks": list(self.defined_tasks),
                    "attempted_runs": list(undefined_runs)
                }
            )

    def _find_last_task_line(self, tasks: list[dict[str, Any]]) -> int:
        """Find the line number of the last task in the program."""
        if not self.source_code:
            return 1
            
        lines = self.source_code.split('\n')
        for i in range(len(lines) - 1, -1, -1):
            if any(f'task "{task["name"]}"' in lines[i] for task in tasks):
                return i + 1
        return 1

    def _get_context_lines(self, error_line: int, context_size: int = 2) -> str:
        """Get source code context around the error line."""
        if not self.source_code:
            return ""
            
        lines = self.source_code.split('\n')
        start = max(0, error_line - context_size - 1)
        end = min(len(lines), error_line + context_size)
        
        context_lines = []
        for i in range(start, end):
            line_num = i + 1
            prefix = '->' if line_num == error_line else '  '
            context_lines.append(f"{prefix} {line_num}: {lines[i]}")
        
        return '\n'.join(context_lines)