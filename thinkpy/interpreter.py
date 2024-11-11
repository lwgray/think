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
            'print': print,
        }

    def execute(self, ast):
        """Execute a parsed ThinkPy program"""
        if self.explain_mode:
            print(f"Starting execution of program with objective: {ast['objective']}")
        
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
            print(f"Executing task: {task_name}")
        
        # Execute each step/subtask in the task
        for item in task['body']:
            if item.get('type') == 'step':
                self.execute_step(item)
            elif item.get('type') == 'subtask':
                self.execute_subtask(item['name'])

    def execute_step(self, step):
        """Execute a single step"""
        if self.explain_mode:
            print(f"Executing step: {step['name']}")
        
        for statement in step['statements']:
            self.execute_statement(statement)

    def execute_subtask(self, subtask_name):
        """Execute a named subtask"""
        if subtask_name not in self.subtasks:
            raise RuntimeError(f"Subtask '{subtask_name}' not found")
        
        subtask = self.subtasks[subtask_name]
        if self.explain_mode:
            print(f"Executing subtask: {subtask_name}")
        
        for statement in subtask['statements']:
            result = self.execute_statement(statement)
            if isinstance(result, dict) and result.get('type') == 'return':
                return result['value']

    def execute_statement(self, statement):
        """Execute a single statement"""
        stmt_type = statement.get('type')
        
        if stmt_type == 'assignment':
            value = self.evaluate_expression(statement['value'])
            self.state[statement['variable']] = value
            
        elif stmt_type == 'function_call':
            return self.execute_function_call(statement)
            
        elif stmt_type == 'return':
            value = self.evaluate_expression(statement['value'])
            return {'type': 'return', 'value': value}
            
        elif stmt_type == 'decide':
            return self.execute_decide(statement)
            
        elif stmt_type == 'repeat':
            return self.execute_repeat(statement)

    def evaluate_expression(self, expr):
        """Evaluate an expression and return its value"""
        if isinstance(expr, (int, str)):
            return expr
            
        if isinstance(expr, dict):
            if expr.get('type') == 'list':
                return [self.evaluate_expression(item) for item in expr['items']]
                
            elif expr.get('type') == 'operation':
                return self.evaluate_operation(expr)
                
            elif expr.get('type') == 'function_call':
                return self.execute_function_call(expr)
                
        # Handle variable references
        if isinstance(expr, str) and expr in self.state:
            return self.state[expr]
            
        return expr

    def evaluate_operation(self, operation):
        """Evaluate a mathematical or logical operation"""
        left = self.evaluate_expression(operation['left'])
        right = self.evaluate_expression(operation['right'])
        op = operation['operator']
        
        if op == '+': return left + right
        elif op == '-': return left - right
        elif op == '*': return left * right
        elif op == '/': return left / right
        else:
            raise RuntimeError(f"Unknown operator: {op}")

    def execute_function_call(self, func_call):
        """Execute a function call"""
        func_name = func_call['name']
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

    def execute_repeat(self, repeat_stmt):
        """Execute a repeat statement"""
        times = repeat_stmt['times']
        for _ in range(times):
            for statement in repeat_stmt['body']:
                self.execute_statement(statement)

# Example usage with the parser
if __name__ == "__main__":
    from parser import parse_thinkpy
    
    # Example ThinkPy program
    program = '''
    objective "Calculate average temperature"

    task "Data Collection" {
        step "Get readings" {
            temps = [72, 75, 68, 70, 73]
        }
    }

    task "Analysis" {
        subtask "Calculate Average" {
            total = sum(temps)
            avg = total / 5
            return avg
        }
    }

    run "Data Collection"
    run "Analysis"
    '''
    
    # Parse and execute the program
    ast = parse_thinkpy(program)
    interpreter = ThinkPyInterpreter(explain_mode=True)
    interpreter.execute(ast)
    
    # Print final state
    print("\nFinal program state:")
    print(interpreter.state)