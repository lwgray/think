class ThinkError(Exception):
    """Base class for Think errors"""
    def __init__(self, message, line=None, column=None, context=None):
        self.message = message
        self.line = line
        self.column = column
        self.context = context
        super().__init__(self.format_message())
    
    def format_message(self):
        msg = f"Think Error: {self.message}"
        if self.line is not None:
            msg += f"\nLine: {self.line}"
        if self.column is not None:
            msg += f"\nColumn: {self.column}"
        if self.context is not None:
            msg += f"\nContext: {self.context}"
        return msg

class ThinkParserError(ThinkError):
    """Error during parsing phase"""
    def __init__(self, message, line=None, column=None, token=None, source_snippet=None):
        self.token = token
        self.source_snippet = source_snippet
        context = self.format_context()
        super().__init__(message, line, column, context)
    
    def format_context(self):
        context = []
        if self.token:
            context.append(f"Near token: '{self.token}'")
        if self.source_snippet:
            context.append(f"Source code:\n{self.source_snippet}")
        return "\n".join(context)

class ThinkPyRuntimeError(ThinkError):
    """Error during program execution"""
    def __init__(self, message, task=None, step=None, variables=None):
        self.task = task
        self.step = step
        self.variables = variables
        context = self.format_context()
        super().__init__(message, context=context)
    
    def format_context(self):
        context = []
        if self.task:
            context.append(f"In task: '{self.task}'")
        if self.step:
            context.append(f"In step/subtask: '{self.step}'")
        if self.variables:
            context.append("Current variable state:")
            for var, value in self.variables.items():
                context.append(f"  {var} = {value}")
        return "\n".join(context)