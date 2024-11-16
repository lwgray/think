class ThinkPyInterpreter:
    def __init__(self, explain_mode=False, format_style="default", max_iterations_shown=5):
        self.state = {}  # Variable storage
        self.explain_mode = explain_mode
        self.format_style = format_style
        self.indent_level = 0
        self.tasks = {}  # Store tasks for later execution
        self.subtasks = {}  # Store subtasks
        self.max_iterations_shown = max_iterations_shown
        self.iteration_count = 0
        
        # ANSI color codes for prettier output
       # ANSI Color Code Constants
        self.colors = {
            # Original bright colors you liked
            'blue': '\033[94m',        # Tasks
            'yellow': '\033[93m',      # Steps
            'red': '\033[91m',         # Variables
            'green': '\033[92m',       # Output/Subtasks
            'white': '\033[37m',       # Info
            # New colors for other statements
            'cyan': '\033[96m',        # Loops
            'light_cyan': '\033[36m',  # Iterations
            'light_green': '\033[32m', # Complete
            'magenta': '\033[95m',     # Decisions
            'light_magenta': '\033[35m', # Checks/Branches
            'light_blue': '\033[34m',  # Results
            # Text styles
            'bold': '\033[1m',
            'underline': '\033[4m',
            'end': '\033[0m'
        }
        
        # Add the statement color mapping
        self.statement_colors = {
            'PROGRAM': self.colors['blue'],
            'TASK': self.colors['blue'],
            'STEP': self.colors['yellow'],
            'VARIABLE': self.colors['red'],
            'OUTPUT': self.colors['green'],
            'SUBTASK': self.colors['green'],
            'INFO': self.colors['white'],
            'LOOP': self.colors['cyan'],
            'ITERATION': self.colors['light_cyan'],
            'COMPLETE': self.colors['light_green'],
            'DECISION': self.colors['magenta'],
            'CHECK': self.colors['light_magenta'],
            'RESULT': self.colors['light_blue'],
            'BRANCH': self.colors['light_magenta']
        }

        # Built-in functions
        self.builtins = {
            'sum': sum,
            'len': len,
            'print': self.print_wrapper,  # Use wrapper for print
        }

        self.state['True'] = True
        self.state['False'] = False

    def format_message(self, category, message):
        """Format explanatory messages based on the chosen style"""
        indent = "  " * self.indent_level
        
        if self.format_style == "minimal":
            return f"{indent}{category}: {message}"
            
        elif self.format_style == "detailed":
            separator = "─" * 40
            return f"\n{indent}{separator}\n{indent}{category}: {message}\n{indent}{separator}\n"
            
        elif self.format_style == "color":
            color = self.statement_colors.get(category.upper(), self.colors['white'])
            return f"{indent}{color}{self.colors['bold']}{category}{self.colors['end']}: {message}"
            
        elif self.format_style == "markdown":
            markdown_levels = {
                "TASK": "##",
                "SUBTASK": "###",
                "STEP": "####",
                "VARIABLE": "*",
            }
            level = markdown_levels.get(category.upper(), "-")
            return f"{indent}{level} {message}"
        
        elif self.format_style == "educational":
            category_icons = {
                "DECISION": "🤔",
                "CHECK": "⚖️",
                "RESULT": "✨",
                "BRANCH": "↪️",
                "LOOP": "🔄",
                "ITERATION": "👉",
                "INFO": "ℹ️",
                "COMPLETE": "✅",
                "VARIABLE": "📝",
            }
            icon = category_icons.get(category.upper(), "•")
            return f"{indent}{icon} {message}"
            
        else:  # default style
            return f"{indent}[{category}] {message}"

    def explain_print(self, category, message):
        """Print explanatory message if in explain mode"""
        if self.explain_mode:
            print(self.format_message(category, message))

    def print_wrapper(self, *args):
        """Wrapper for print function to properly handle variable references and formatting"""
        # Convert all arguments to their string representation
        str_args = []
        for arg in args:
            if isinstance(arg, bool):
                str_args.append(str(arg))
            elif isinstance(arg, float):
                # Format floats to avoid scientific notation for small numbers
                str_args.append(f"{arg:.6f}".rstrip('0').rstrip('.'))
            elif isinstance(arg, (list, dict)):
                str_args.append(str(arg))
            else:
                str_args.append(str(arg))
                
        # Format the output string
        output = " ".join(str_args)
        indent = "  " * self.indent_level
        
        if self.format_style == "minimal":
            print(f"{indent}OUTPUT: {output}")
        
        elif self.format_style == "detailed":
            separator = "─" * 40
            print(f"\n{indent}{separator}\n{indent}OUTPUT: {output}\n{indent}{separator}\n")
        
        elif self.format_style == "color":
            output_color = self.statement_colors.get('OUTPUT', self.colors['green'])
            print(f"{indent}{output_color}{self.colors['bold']}OUTPUT{self.colors['end']}: {output}")
        
        elif self.format_style == "markdown":
            print(f"{indent}> {output}")
        
        elif self.format_style == "educational":
            print(f"{indent}📤 Output: {output}")
        
        else:  # default style
            print(f"{indent}[OUTPUT] {output}")

    def execute(self, ast):
        """Execute a parsed ThinkPy program"""
        if self.explain_mode:
            program_header = "PROGRAM EXECUTION"
            if self.format_style == "detailed":
                separator = "=" * 60
                print(f"\n{separator}\n{program_header}: {ast['objective']}\n{separator}\n")
            else:
                self.explain_print("PROGRAM", ast['objective'])
        
        # First pass: register all tasks and subtasks
        self.register_tasks(ast['tasks'])
        
        # Second pass: execute the run list
        for task_name in ast['runs']:
            self.execute_task(task_name)

    def register_tasks(self, tasks):
        """Register all tasks and subtasks for later execution"""
        for task in tasks:
            self.tasks[task['name']] = task
            
            # Register any subtasks within this task
            for item in task['body']:
                if item.get('type') == 'subtask':
                    self.subtasks[item['name']] = item

    def execute_task(self, task_name):
        """Execute a named task"""
        if task_name not in self.tasks:
            raise RuntimeError(f"Task '{task_name}' not found")
        
        task = self.tasks[task_name]
        self.explain_print("TASK", f"Executing {task_name}")
        self.indent_level += 1
        
        # Execute each step/subtask in the task
        for item in task['body']:
            if item.get('type') == 'step':
                self.execute_step(item)
            elif item.get('type') == 'subtask':
                self.execute_subtask(item['name'])
        
        self.indent_level -= 1

    def execute_step(self, step):
        """Execute a single step"""
        self.explain_print("STEP", f"Executing {step['name']}")
        self.indent_level += 1
        
        for statement in step['statements']:
            self.execute_statement(statement)
        
        self.indent_level -= 1

    def execute_subtask(self, subtask_name):
        """Execute a named subtask"""
        if subtask_name not in self.subtasks:
            raise RuntimeError(f"Subtask '{subtask_name}' not found")
        
        subtask = self.subtasks[subtask_name]
        self.explain_print("SUBTASK", f"Executing {subtask_name}")
        self.indent_level += 1
        
        for statement in subtask['statements']:
            result = self.execute_statement(statement)
            if isinstance(result, dict) and result.get('type') == 'return':
                self.indent_level -= 1
                return result['value']
        
        self.indent_level -= 1

    def execute_statement(self, statement):
        """Execute a single statement"""
        stmt_type = statement.get('type')
        
        if stmt_type == 'assignment':
            value = self.evaluate_expression(statement['value'])
            self.state[statement['variable']] = value
            self.explain_print("VARIABLE", f"Assigned {value} to {statement['variable']}")
        
        elif stmt_type == 'for_loop':
            return self.execute_for_loop(statement)
        
        elif stmt_type == 'function_call':
            return self.execute_function_call(statement)
            
        elif stmt_type == 'return':
            value = self.evaluate_expression(statement['value'])
            return {'type': 'return', 'value': value}
            
        elif stmt_type == 'decide':
            return self.execute_decide(statement)

    def evaluate_expression(self, expr):
        """Evaluate an expression and return its value"""
        # Handle direct values
        if isinstance(expr, (int, float, bool)):
            return expr
            
        # Handle string literals (already stripped of quotes by parser)
        if isinstance(expr, str):
            if expr in self.state:
                return self.state[expr]
            return expr
            
        # Handle complex expressions
        if isinstance(expr, dict):
            expr_type = expr.get('type')
            
            if expr_type == 'list':
                return [self.evaluate_expression(item) for item in expr['items']]
                
            elif expr_type == 'operation':
                return self.evaluate_operation(expr)
                
            elif expr_type == 'function_call':
                return self.execute_function_call(expr)
                
        return expr

    def evaluate_operation(self, operation):
        """Evaluate a mathematical or logical operation"""
        left = self.evaluate_expression(operation['left'])
        right = self.evaluate_expression(operation['right'])
        op = operation['operator']
        
        if op == '+': 
            # Handle string concatenation
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        elif op == '-': return float(left - right)
        elif op == '*': return float(left * right)
        elif op == '/': 
            if right == 0:
                raise RuntimeError("Division by zero")
            return float(left) / float(right)
        elif op == '==': return left == right
        elif op == '!=': return left != right
        elif op == '<': return left < right
        elif op == '>': return left > right
        elif op == '<=': return left <= right
        elif op == '>=': return left >= right
        else:
            raise RuntimeError(f"Unknown operator: {op}")

    def execute_function_call(self, func_call):
        """Execute a function call"""
        func_name = func_call['name']
        # Evaluate all arguments before passing them to the function
        args = [self.evaluate_expression(arg) for arg in func_call['arguments']]
        
        # Check for built-in functions
        if func_name in self.builtins:
            return self.builtins[func_name](*args)
            
        # Check for subtasks used as functions
        if func_name in self.subtasks:
            return self.execute_subtask(func_name)
            
        raise RuntimeError(f"Unknown function: {func_name}")

    def execute_decide(self, decide_stmt):
        """Execute a decide (if/else) statement with educational explanations"""
        if self.explain_mode:
            self.explain_print("DECISION", "Starting a conditional block")
            self.indent_level += 1
            
        for condition in decide_stmt['conditions']:
            if condition['type'] == 'if' or condition['type'] == 'elif':
                # Extract the actual condition (before 'then')
                if isinstance(condition['condition'], dict) and condition['condition'].get('type') == 'operation':
                    left = self.evaluate_expression(condition['condition']['left'])
                    right = self.evaluate_expression(condition['condition']['right'])
                    op = condition['condition']['operator']
                    
                    if self.explain_mode:
                        self.explain_print("CHECK", f"Checking if {left} {op} {right}")
                    
                    condition_value = self.evaluate_operation({
                        'type': 'operation',
                        'left': left,
                        'right': right,
                        'operator': op
                    })
                    
                    if self.explain_mode:
                        self.explain_print("RESULT", f"Condition evaluates to: {condition_value}")
                else:
                    condition_value = self.evaluate_expression(condition['condition'])
                    if self.explain_mode:
                        self.explain_print("CHECK", f"Checking condition: {condition['condition']}")
                        self.explain_print("RESULT", f"Condition evaluates to: {condition_value}")
                
                if condition_value:
                    if self.explain_mode:
                        self.explain_print("BRANCH", f"Taking {'if' if condition['type'] == 'if' else 'elif'} branch")
                        self.indent_level += 1
                    
                    for statement in condition['body']:
                        result = self.execute_statement(statement)
                        if isinstance(result, dict) and result.get('type') == 'return':
                            if self.explain_mode:
                                self.indent_level -= 2
                            return result
                    
                    if self.explain_mode:
                        self.indent_level -= 1
                    return
            else:  # else clause
                if self.explain_mode:
                    self.explain_print("BRANCH", "No conditions were true, taking else branch")
                    self.indent_level += 1
                
                for statement in condition['body']:
                    result = self.execute_statement(statement)
                    if isinstance(result, dict) and result.get('type') == 'return':
                        if self.explain_mode:
                            self.indent_level -= 2
                        return result
                
                if self.explain_mode:
                    self.indent_level -= 1
                return
        
        if self.explain_mode:
            self.indent_level -= 1

    def execute_for_loop(self, loop_stmt):
        """Execute a for loop with educational explanations"""
        iterator_name = loop_stmt['iterator']
        iterable_name = loop_stmt['iterable']

        if iterable_name not in self.state:
            raise RuntimeError(f"Undefined variable: {iterable_name}")
        
        iterable = self.state[iterable_name]
        if not hasattr(iterable, '__iter__'):
            raise RuntimeError(f"{iterable_name} is not a collection we can iterate over")
        
        if self.explain_mode:
            self.explain_print("LOOP", f"Starting a loop that will go through each item in {iterable_name}")
            self.explain_print("INFO", f"Total number of items to process: {len(iterable)}")
            self.indent_level += 1
            self.iteration_count = 0

        for i, item in enumerate(iterable):
            self.state[iterator_name] = item
            
            if self.explain_mode:
                # Only show details for the first few iterations
                if i < self.max_iterations_shown:
                    self.explain_print("ITERATION", f"Loop #{i + 1}: {iterator_name} = {item}")
                elif i == self.max_iterations_shown:
                    remaining = len(iterable) - self.max_iterations_shown
                    self.explain_print("INFO", f"... {remaining} more iterations will be processed ...")
                elif i == len(iterable) - 1:
                    self.explain_print("INFO", f"Final iteration completed: {iterator_name} = {item}")
            
            for statement in loop_stmt['body']:
                result = self.execute_statement(statement)
                if isinstance(result, dict) and result.get('type') == 'return':
                    if self.explain_mode:
                        self.indent_level -= 1
                    return result
        
        if self.explain_mode:
            self.explain_print("COMPLETE", f"Loop finished after processing {len(iterable)} items")
            self.indent_level -= 1


if __name__ == "__main__":
    from parser import parse_thinkpy
    
    # Example ThinkPy program
    program = '''
    objective "Test different formatting styles"

    task "Greeting" {
        step "Set message" {
            message = "Hello, World!"
            print(message)
        }
        
        step "Loop example" {
            items = ["a", "b", "c"]
            for item in items {
                print(item)
            }
        }
    }

    run "Greeting"
    '''
    
    # Try different formatting styles
    styles = ["default", "minimal", "detailed", "color", "markdown", "educational"]
    
    for style in styles:
        print(f"\nTrying style: {style}")
        print("-" * 40)
        
        ast = parse_thinkpy(program)
        interpreter = ThinkPyInterpreter(explain_mode=True, format_style=style)
        interpreter.execute(ast)
        
        # Print final state
        print("\nFinal program state:")
        print(interpreter.state)