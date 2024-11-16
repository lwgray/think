class ThinkPyInterpreter:
    def __init__(self, explain_mode=False):
        self.state = {}  # Variable storage
        self.explain_mode = explain_mode
        self.tasks = {}  # Store tasks for later execution
        self.subtasks = {}  # Store subtasks
        
        # Built-in functions
        self.builtins = {
            'sum': sum,
            'len': len,
            'print': self.print_wrapper,  # Use wrapper for print
        }

        self.state['True'] = True
        self.state['False'] = False

    def print_wrapper(self, *args):
        """Wrapper for print function to properly handle variable references"""
        # Convert all arguments to their string representation
        str_args = []
        for arg in args:
            if isinstance(arg, bool):
                str_args.append(str(arg))
            elif isinstance(arg, (list, dict)):
                str_args.append(str(arg))
            else:
                str_args.append(str(arg))
        print(*str_args)

    def execute(self, ast):
        """Execute a parsed ThinkPy program"""
        if self.explain_mode:
            print(f"Starting execution of program with objective: {ast['objective']}\n\n")
        
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
        if self.explain_mode:
            print(f"Executing task: {task_name}\n")
        
        # Execute each step/subtask in the task
        for item in task['body']:
            if item.get('type') == 'step':
                self.execute_step(item)
            elif item.get('type') == 'subtask':
                self.execute_subtask(item['name'])

    def execute_step(self, step):
        """Execute a single step"""
        if self.explain_mode:
            print(f"Executing step: {step['name']}\n")
        
        for statement in step['statements']:
            self.execute_statement(statement)

    def execute_subtask(self, subtask_name):
        """Execute a named subtask"""
        if subtask_name not in self.subtasks:
            raise RuntimeError(f"Subtask '{subtask_name}' not found")
        
        subtask = self.subtasks[subtask_name]
        if self.explain_mode:
            print(f"Executing subtask: {subtask_name}\n")
        
        for statement in subtask['statements']:
            result = self.execute_statement(statement)
            if isinstance(result, dict) and result.get('type') == 'return':
                return result['value']

    def execute_statement(self, statement):
        """Execute a single statement"""
        
        # print(f"DEBUG: Statement received: {statement}")
        # print(f"DEBUG: Statement type: {type(statement)}")
        
        # if isinstance(statement, str):
        #     print(f"DEBUG: Got string instead of dict: {statement}")
        #     # Handle string case or raise more informative error
        #     raise RuntimeError(f"Expected dictionary for statement, got string: {statement}")
            
        stmt_type = statement.get('type')
        
        if stmt_type == 'assignment':
            value = self.evaluate_expression(statement['value'])
            self.state[statement['variable']] = value
            if self.explain_mode:
                print(f"Assigned {value} to {statement['variable']}\n")
        
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
        elif op == '-': return left - right
        elif op == '*': return left * right
        elif op == '/': return left / right
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
        """Execute a decide (if/else) statement"""
        for condition in decide_stmt['conditions']:
            if condition['type'] == 'if' or condition['type'] == 'elif':
                if self.evaluate_expression(condition['condition']):
                    for statement in condition['body']:
                        self.execute_statement(statement)
                    return
            else:  # else clause
                for statement in condition['body']:
                    self.execute_statement(statement)
                return

    def execute_for_loop(self, loop_stmt):
        """Execute a for loop iterating over a collection
        Args:
            loop_stmt: Dictionary containing:
                - iterator: Name of each item in iteration
                - iterable: Name of the collection to iterate over
                - body: List of statements to execute in each iteration
        Raises:
            RuntimeError: If iterable doesn't exist or isn't iterable
        """
        iterator_name = loop_stmt['iterator']
        iterable_name = loop_stmt['iterable']

        if iterable_name not in self.state:
            raise RuntimeError(f"Undefined variable: {iterable_name}")
        
        iterable = self.state[iterable_name]
        if not hasattr(iterable, '__iter__'):
            raise RuntimeError(f"{iterable_name} is not a collection we can iteratoe over")
        
        if self.explain_mode:
            print(f"Starting iteration over {iterable_name}\n")

        for item in iterable:
            # Set the iterator variable for this iteration
            self.state[iterator_name] = item

            if self.explain_mode:
                print(f"Processing {iterator_name}: {item}")

            # Execute each statement in the loop body    
            for statement in loop_stmt['body']:
                self.execute_statement(statement)

if __name__ == "__main__":
    from parser import parse_thinkpy
    
    # Example ThinkPy program
    program = '''
    objective "Test string handling"

    task "Greeting" {
        step "Set message" {
            message = "Hello, World!"
            print(message)
        }
    }

    run "Greeting"
    '''
    
    # Parse and execute the program
    ast = parse_thinkpy(program)
    interpreter = ThinkPyInterpreter(explain_mode=True)
    interpreter.execute(ast)
    
    # Print final state
    print("\nFinal program state:")
    print(interpreter.state)