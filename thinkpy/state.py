from parser import parse_thinkpy
from interpreter import ThinkPyInterpreter
    
# Example ThinkPy program
program = '''
objective "Test list operations"
task "Lists":
    step "Process":
        items = [1,2,3]
        for index, value in enumerate(items):
            print(value)
        end
run "Lists"'''
    
# Try different formatting styles
styles = ["default", "minimal", "detailed", "color", "markdown", "educational"]
    
ast = parse_thinkpy(program)
print("AST:", ast)
interpreter = ThinkPyInterpreter(explain_mode=True, format_style=styles[0])
interpreter.execute(ast)
print(type(interpreter.state['items']))