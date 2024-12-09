from .errors import ThinkRuntimeError, ThinkError
from .validator import ThinkValidator


class ThinkInterpreter:
    def __init__(self, explain_mode=False, format_style="default", max_iterations_shown=5, source_code=None):
        self.state = {}  # Variable storage
        self.explain_mode = explain_mode
        self.format_style = format_style
        self.indent_level = 0
        self.tasks = {}  # Store tasks for later execution
        self.subtasks = {}  # Store subtasks
        self.source_code = source_code
        self.max_iterations_shown = max_iterations_shown
        self.iteration_count = 0
        self.current_task = None
        self.current_step = None
        
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
            'print': self.print_wrapper,
            'range': range,
            'enumerate': enumerate,
        }


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
            if isinstance(arg, dict) and arg.get('type') == 'string_literal':
                str_args.append(arg['value'])
            elif isinstance(arg, bool):
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
        """Execute a parsed Think program"""
        try:
            validator = ThinkValidator()
            validator.validate_program(ast, self.source_code)

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
        
        except ThinkError as e:
            raise
        except Exception as e:
            # Convert other exceptions to ThinkPythonError
            raise ThinkRuntimeError(
                message=str(e),
                task=self.current_task if hasattr(self, 'current_task') else None,
                step=self.current_step if hasattr(self, 'current_step') else None,
                variables=self.state if hasattr(self, 'state') else {}
            )

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
            raise ThinkRuntimeError(
                message=f"Task '{task_name}' not found",
                task=task_name,
                step=None,
                variables={
                    "available_tasks": list(self.tasks.keys())
                }
            )
        
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
            raise ThinkRuntimeError(
                message=f"Subtask '{subtask_name}' not found",
                task=self.current_task,
                step="subtask execution",
                variables={
                    "attempted_subtask": subtask_name,
                    "available_subtasks": list(self.subtasks.keys())
                })
        
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
            if isinstance(value, dict) and value.get('type') == 'string_literal':
                value = value['value']
            self.state[statement['variable']] = value
            display_value = f'"{value}"' if isinstance(value, str) else str(value)
            self.explain_print("VARIABLE", f"Assigned {display_value} to {statement['variable']}")
        
        elif stmt_type == 'enumerate_loop':
            if statement['iterable'] not in self.state:
                raise ThinkRuntimeError(f"Undefined variable: {statement['iterable']}")
            
            iterable = self.state[statement['iterable']]
            if not hasattr(iterable, '__iter__'):
                raise ThinkRuntimeError(message=f"{statement['iterable']} is not a collection we can iterate over",
                    task=self.current_task,
                    step=f"enumerate loop over {statement['iterable']}",
                    variables={
                        "iterable_name": statement['iterable'],
                        "iterable_type": self.state[statement['iterable']].__name__,
                        "current_variables": self.state
                    }
                )
            
            if self.explain_mode:
                self.explain_print("LOOP", f"Starting enumerate loop over {statement['iterable']}")
                self.indent_level += 1
            
            for i, value in enumerate(iterable):
                self.state[statement['index']] = i
                self.state[statement['element']] = value
                
                if self.explain_mode and i < self.max_iterations_shown:
                    self.explain_print("ITERATION", f"Loop #{i + 1}: {statement['index']} = {i}, {statement['element']} = {value}")
                
                for body_statement in statement['body']:
                    result = self.execute_statement(body_statement)
                    if isinstance(result, dict) and result.get('type') == 'return':
                        if self.explain_mode:
                            self.indent_level -= 1
                        return result
            
            if self.explain_mode:
                self.explain_print("COMPLETE", f"Loop finished")
                self.indent_level -= 1
        
        elif stmt_type == 'for_loop':
            return self.execute_for_loop(statement)
        
        elif stmt_type == 'range_loop':
            return self.execute_range_loop(statement)
        
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
                
        # Handle complex expressions
        if isinstance(expr, dict):
            expr_type = expr.get('type')
            
            # Handle string literals explicitly
            if expr_type == 'string_literal':
                return expr['value']
                
            if expr_type == 'list':
                evaluated_items = []
                for item in expr['items']:
                    value = self.evaluate_expression(item)
                    if isinstance(value, dict) and value.get('type') == 'string_literal':
                        value = value['value']
                    evaluated_items.append(value)
                return evaluated_items
            
            elif expr_type == 'dict':
                return self.evaluate_dict(expr.get('entries', []))
            
            elif expr_type == 'index':
                container = self.evaluate_expression(expr['container'])
                key = self.evaluate_expression(expr['key'])
                
                # Convert string literal to string if it's being used as a key
                if isinstance(key, dict) and key.get('type') == 'string_literal':
                    key = key['value']

                if isinstance(container, (dict, list)):
                    try:
                        if isinstance(container, list):
                            key = int(key)
                        return container[key]
                    except (KeyError, IndexError, ValueError) as e:
                        raise ThinkRuntimeError(
                            message=f"Invalid index/key: {key} for container {container}",
                            task=self.current_task,
                            step=self.current_step,
                            variables={
                                "container_type": type(container).__name__,
                                "container_value": container,
                                "attempted_key": key,
                                "valid_keys": list(container.keys()) if isinstance(container, dict) else f"0-{len(container)-1}"
                            }
                        )
                else:
                    raise ThinkRuntimeError(
                        message=f"Cannot index into type: {type(container)}",
                        task=self.current_task,
                        step=self.current_step,
                        variables={
                            "attempted_type": type(container).__name__,
                            "indexable_types": ["list", "dict", "string"],
                            "value_attempted": str(container)
                        }
                    )
            
            elif expr_type == 'operation':
                return self.evaluate_operation(expr)
                
            elif expr_type == 'function_call':
                return self.execute_function_call(expr)
                    
        # Handle variable references (strings that aren't in dict form)
        if isinstance(expr, str):
            if expr in self.state:
                return self.state[expr]
            elif expr not in self.state:
                raise ThinkRuntimeError(
                    message=f"Undefined variable: {expr}",
                    task=self.current_task,
                    step=self.current_step,
                    variables={
                        "attempted_variable": expr,
                        "defined_variables": list(self.state.keys())
                    })
                
        return expr

    def evaluate_operation(self, operation):
        """Evaluate a mathematical or logical operation"""
        op = operation['operator']

        if op == 'uminus':
            operand = self.evaluate_expression(operation['operand'])
            return -operand
        
        left = self.evaluate_expression(operation['left'])
        right = self.evaluate_expression(operation['right'])

         # Handle string literals - extract actual string values
        if isinstance(left, dict) and left.get('type') == 'string_literal':
            left = left['value']
        if isinstance(right, dict) and right.get('type') == 'string_literal':
            right = right['value']

        if op == '+': 
            # Handle string concatenation
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            elif isinstance(left, list):
                if isinstance(right, list):
                    return left + right
                else:
                    raise ThinkRuntimeError(
                        message=f"Cannot concatenate list with non-list",
                        task=self.current_task,
                        step=self.current_step,
                        variables={
                            "left_type": type(left).__name__,
                            "right_type": type(right).__name__,
                            "left_value": left,
                            "right_value": right
                        })
            elif isinstance(right, list):
                if isinstance(left, list):
                    return left + right
                else:
                    raise ThinkRuntimeError(
                        message=f"Cannot concatenate list with non-list",
                        task=self.current_task,
                        step=self.current_step,
                        variables={
                            "operation": "concatenation",
                            "left_type": type(left).__name__,
                            "right_type": type(right).__name__,
                            "left_value": left,
                            "expected_type": "list"
                        })
            return left + right
        elif op == '-': return float(left - right)
        elif op == '*': return float(left * right)
        elif op == '/': 
            if right == 0:
                raise ThinkRuntimeError(
                    message="Division by zero",
                    task=self.current_task,
                    step=self.current_step,
                    variables={
                        "operation": "division",
                        "left_operand": left,
                        "right_operand": right,
                        "current_variables": self.state
                    })
            return float(left) / float(right)
        elif op == '==': return left == right
        elif op == '!=': return left != right
        elif op == '<': return left < right
        elif op == '>': return left > right
        elif op == '<=': return left <= right
        elif op == '>=': return left >= right
        else:
            raise ThinkRuntimeError(
                message=f"Unknown operator: {op}",
                task=self.current_task,
                step=self.current_step,
                variables={
                    "operation": "unknown",
                    "left_operand": left,
                    "right_operand": right,
                    "supported_operators": ['+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>='],
                })

    def execute_function_call(self, func_call):
        """Execute a function call"""
        func_name = func_call['name']
        # Evaluate all arguments before passing them to the function
        args = [self.evaluate_expression(arg) for arg in func_call['arguments']]

        # Special handling for range function
        if func_name == 'range':
            if not args:
                raise ThinkRuntimeError(message="range() function requires at least one argument",
                                        task=self.current_task,
                                        step=self.current_step,
                                        variables={
                                            "provided_args": len(args),
                                            "minimum_args": 1,
                                            "function": "range"
                                        })
            end = args[0]
            if not isinstance(end, (int, float)):
                raise ThinkRuntimeError(
                    message=f"range() argument must be a number",
                    task=self.current_task,
                    step=self.current_step,
                    variables={
                        "provided_type": type(end).__name__,
                        "provided_value": end,
                        "expected_type": "number (int or float)"
                    })
            return range(int(end))
        
        # Check for built-in functions
        if func_name in self.builtins:
            return self.builtins[func_name](*args)
            
        # Check for subtasks used as functions
        if func_name in self.subtasks:
            return self.execute_subtask(func_name)
        
        # If not found, try converting the function name to possible subtask names
        converted_name = func_name.replace('_', ' ').title()
        if converted_name in self.subtasks:
            return self.execute_subtask(converted_name)
        
        raise ThinkRuntimeError(
            message=f"Unknown function: {func_name}",
            task=self.current_task,
            step=self.current_step,
            variables={
                "attempted_function": func_name,
                "available_functions": list(self.builtins.keys()) + list(self.subtasks.keys()),
                "current_variables": self.state
            })

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
        iterable_spec = loop_stmt['iterable']
        
        if isinstance(iterable_spec, dict) and iterable_spec['type'] == 'enumerate':
            # Handle enumerate case
            if iterable_spec['iterable'] not in self.state:
                raise ThinkRuntimeError(f"Undefined variable: {iterable_spec['iterable']}")
            
            iterable = enumerate(self.state[iterable_spec['iterable']])
            value_var = iterable_spec['value_var']
        else:
            # Handle normal iteration
            if iterable_spec not in self.state:
                raise ThinkRuntimeError(
                    message=f"Undefined variable in for loop: {iterable_spec}",
                    task=self.current_task,
                    step="for loop initialization",
                    variables={
                        "attempted_variable": iterable_spec,
                        "defined_variables": list(self.state.keys())
                    })
            
            iterable = self.state[iterable_spec]
            
        if not hasattr(iterable, '__iter__'):
            raise ThinkRuntimeError(message=f"{iterable_spec} is not a collection we can iterate over",
                                    task=self.current_task,
                                    step="for loop iteration",
                                    variables={
                                        "iterable_name": iterable_spec,
                                        "iterable_type": type(self.state.get(iterable_spec)).__name__,
                                        "iterable_value": self.state.get(iterable_spec),
                                        "supported_types": ["list", "dict", "string", "range"]
                                    })
        
        if self.explain_mode:
            self.explain_print("LOOP", f"Starting a loop that will go through each item in {iterable_spec}")
            self.indent_level += 1
            self.iteration_count = 0

        for item in iterable:
            if isinstance(iterable_spec, dict) and iterable_spec['type'] == 'enumerate':
                # For enumerate, item is a tuple of (index, value)
                self.state[iterator_name] = item[0]
                self.state[value_var] = item[1]
                
                if self.explain_mode:
                    # Only show details for the first few iterations
                    if self.iteration_count < self.max_iterations_shown:
                        self.explain_print("ITERATION", 
                            f"Loop #{self.iteration_count + 1}: {iterator_name} = {item[0]}, {value_var} = {item[1]}")
            else:
                self.state[iterator_name] = item
                
                if self.explain_mode:
                    # Only show details for the first few iterations
                    if self.iteration_count < self.max_iterations_shown:
                        self.explain_print("ITERATION", f"Loop #{self.iteration_count + 1}: {iterator_name} = {item}")
            
            if self.explain_mode:
                if self.iteration_count == self.max_iterations_shown:
                    self.explain_print("INFO", "... more iterations will be processed ...")
            
            self.iteration_count += 1
            
            for statement in loop_stmt['body']:
                result = self.execute_statement(statement)
                if isinstance(result, dict) and result.get('type') == 'return':
                    if self.explain_mode:
                        self.indent_level -= 1
                    return result
        
        if self.explain_mode:
            self.explain_print("COMPLETE", f"Loop finished after {self.iteration_count} iterations")
            self.indent_level -= 1
    
    def execute_enumerate_loop(self, loop_stmt):
        """Execute an enumerate loop"""
        index_var = loop_stmt['index']
        value_var = loop_stmt['element']
        iterable_name = loop_stmt['iterable']

        if iterable_name not in self.state:
            raise ThinkRuntimeError(
                message=f"Undefined variable in enumerate: {iterable_name}",
                task=self.current_task,
                step="enumerate loop initialization",
                variables={
                    "attempted_variable": iterable_name,
                    "defined_variables": list(self.state.keys())
                })
        
        iterable = self.state[iterable_name]
        if not hasattr(iterable, '__iter__'):
            raise ThinkRuntimeError(
                message=f"{iterable_name} is not a collection we can enumerate",
                task=self.current_task,
                step="enumerate loop",
                variables={
                    "iterable_name": iterable_name,
                    "iterable_type": type(self.state.get(iterable_name)).__name__,
                    "supported_types": ["list", "dict", "string"],
                    "current_value": self.state.get(iterable_name)
                })
        
        if self.explain_mode:
            self.explain_print("LOOP", f"Starting an enumerate loop over {iterable_name}")
            self.explain_print("INFO", f"Total number of items to process: {len(iterable)}")
            self.indent_level += 1

        for i, value in enumerate(iterable):
            self.state[index_var] = i
            self.state[value_var] = value

            if self.explain_mode:
                if i < self.max_iterations_shown:
                    self.explain_print("ITERATION", f"Loop #{i + 1}: {index_var} = {i}, {value_var} = {value}")
                elif i == self.max_iterations_shown:
                    remaining = len(iterable) - self.max_iterations_shown
                    self.explain_print("INFO", f"... {remaining} more iterations will be processed ...")
                elif i == len(iterable) - 1:
                    self.explain_print("INFO", f"Final iteration completed: {index_var} = {i}, {value_var} = {value}")
            
            for statement in loop_stmt['body']:
                result = self.execute_statement(statement)
                if isinstance(result, dict) and result.get('type') == 'return':
                    if self.explain_mode:
                        self.indent_level -= 1
                    return result

        if self.explain_mode:
            self.explain_print("COMPLETE", f"Loop finished after processing {len(iterable)} items")
            self.indent_level -= 1

    def execute_range_loop(self, loop_stmt):
        """Execute a range loop"""
        iterator = loop_stmt['iterator']
        range_expr = loop_stmt['range']

        # If the range expression is a function call (like len(numbers))
        if isinstance(range_expr, dict) and range_expr.get('type') == 'function_call':
            result = self.execute_function_call(range_expr)
            range_obj = range(result)
        else:
            # Evaluate any other type of expression
            end = self.evaluate_expression(range_expr)
            range_obj = range(end)
        
        if self.explain_mode:
            self.explain_print("LOOP", f"Starting range loop from 0 to {len(range_obj)}")
            self.explain_print("INFO", f"Total iterations: {len(range_obj)}")
            self.indent_level += 1

        for i in range_obj:
            self.state[iterator] = i
            
            if self.explain_mode:
                if i < self.max_iterations_shown:
                    self.explain_print("ITERATION", f"Loop #{i + 1}: {iterator} = {i}")
                elif i == self.max_iterations_shown:
                    remaining = len(range_obj) - self.max_iterations_shown
                    self.explain_print("INFO", f"... {remaining} more iterations will be processed ...")
            
            for statement in loop_stmt['body']:
                result = self.execute_statement(statement)
                
                if isinstance(result, dict) and result.get('type') == 'return':
                    if self.explain_mode:
                        self.indent_level -= 1
                    return result

        if self.explain_mode:
            self.explain_print("COMPLETE", f"Loop finished after {len(range_obj)} iterations")
            self.indent_level -= 1

    def evaluate_dict(self, entries):
        """Evaluate dictionary entries and construct dictionary"""
        result = {}
        for entry in entries:
            key = self.evaluate_expression(entry['key'])
            value = self.evaluate_expression(entry['value'])
            
            # Extract string value if it's a string_literal dict (for both key and value)
            if isinstance(key, dict) and key.get('type') == 'string_literal':
                key = key['value']
            if isinstance(value, dict) and value.get('type') == 'string_literal':
                value = value['value']
                
            result[key] = value
        return result
    
    def evaluate_index(self, expr):
        """Evaluate indexing expression"""
        container = self.evaluate_expression(expr['container'])
        key = self.evaluate_expression(expr['key'])

        if isinstance(container, (dict, list)):
            try:
                return container[key]
            except (KeyError, IndexError) as e:
                raise ThinkRuntimeError(
                    message=f"Invalid index/key: {key}",
                    task=self.current_task,
                    step=self.current_step,
                    variables={
                        "attempted_key": key,
                        "container_type": type(container).__name__,
                        "valid_range": f"0-{len(container)-1}" if isinstance(container, (list, str)) else list(container.keys())
                    })
        else:
            raise ThinkRuntimeError(
                message=f"Cannot index into type: {type(container).__name__}",
                task=self.current_task,
                step=self.current_step,
                variables={
                    "container_type": type(container).__name__,
                    "container_value": str(container),
                    "indexable_types": ["list", "dict", "string"]
                })
    

if __name__ == "__main__":
    from parser import parse_think
    
    # Example Think program
    program = '''
        objective "Test"
        task "Math":
            step "Calculate":
                int_result = 42 + -17
                float_result = 3.14 * -2.5
                sci_result = 1.5e3 / 1e2
                mixed = -42 * 3.14159
                print(int_result)
                print(float_result)
                print(sci_result)
                print(mixed)
    run "Math"
    '''
    # Try different formatting styles
    styles = ["default", "minimal", "detailed", "color", "markdown", "educational"]
        
    ast = parse_think(program)
    interpreter = ThinkInterpreter(explain_mode=True, format_style=styles[0])
    interpreter.execute(ast)
    
    # Print final state
    print("\nFinal program state:")
    print(interpreter.state)