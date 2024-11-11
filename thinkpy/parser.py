import ply.lex as lex
import ply.yacc as yacc

# Lexer tokens
tokens = (
    'OBJECTIVE',
    'TASK',
    'SUBTASK',
    'STEP',
    'RUN',
    'STRING',
    'IDENTIFIER',
    'NUMBER',
    'EQUALS',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'IF',
    'ELSE',
    'THEN',
    'DECIDE',
    'REPEAT',
    'COMMA',
    'RETURN'
)

# Token definitions
t_EQUALS = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','

# Reserved words
reserved = {
    'objective': 'OBJECTIVE',
    'task': 'TASK',
    'subtask': 'SUBTASK',
    'step': 'STEP',
    'run': 'RUN',
    'if': 'IF',
    'else': 'ELSE',
    'then': 'THEN',
    'decide': 'DECIDE',
    'repeat': 'REPEAT',
    'return': 'RETURN'
}

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  # Remove quotes
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignored characters
t_ignore = ' \t\n'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Parser rules
def p_program(p):
    '''program : objective task_list run_list'''
    p[0] = {'objective': p[1], 'tasks': p[2], 'runs': p[3]}

def p_objective(p):
    '''objective : OBJECTIVE STRING'''
    p[0] = p[2]

def p_task_list(p):
    '''task_list : task
                | task task_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_task(p):
    '''task : TASK STRING LBRACE step_or_subtask_list RBRACE'''
    p[0] = {'name': p[2], 'body': p[4]}

def p_step_or_subtask_list(p):
    '''step_or_subtask_list : step
                           | subtask
                           | step step_or_subtask_list
                           | subtask step_or_subtask_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_step(p):
    '''step : STEP STRING LBRACE statement_list RBRACE'''
    p[0] = {'type': 'step', 'name': p[2], 'statements': p[4]}

def p_subtask(p):
    '''subtask : SUBTASK STRING LBRACE statement_list RBRACE'''
    p[0] = {'type': 'subtask', 'name': p[2], 'statements': p[4]}

def p_statement_list(p):
    '''statement_list : statement
                     | statement statement_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_statement(p):
    '''statement : assignment
                | function_call
                | decide_statement
                | repeat_statement
                | return_statement'''
    p[0] = p[1]

def p_return_statement(p):
    '''return_statement : RETURN expression'''
    p[0] = {'type': 'return', 'value': p[2]}

def p_decide_statement(p):
    '''decide_statement : DECIDE LBRACE condition_list RBRACE'''
    p[0] = {'type': 'decide', 'conditions': p[3]}

def p_condition_list(p):
    '''condition_list : condition
                     | condition condition_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_condition(p):
    '''condition : IF expression THEN statement_list
                | ELSE IF expression THEN statement_list
                | ELSE statement_list'''
    if p[1] == 'if':
        p[0] = {'type': 'if', 'condition': p[2], 'body': p[4]}
    elif len(p) == 6:  # else if
        p[0] = {'type': 'elif', 'condition': p[3], 'body': p[5]}
    else:  # else
        p[0] = {'type': 'else', 'body': p[2]}

def p_repeat_statement(p):
    '''repeat_statement : REPEAT NUMBER TIMES LBRACE statement_list RBRACE'''
    p[0] = {'type': 'repeat', 'times': p[2], 'body': p[5]}

def p_assignment(p):
    '''assignment : IDENTIFIER EQUALS expression'''
    p[0] = {'type': 'assignment', 'variable': p[1], 'value': p[3]}

def p_expression(p):
    '''expression : term
                 | expression PLUS term
                 | expression MINUS term
                 | expression TIMES term
                 | expression DIVIDE term'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {'type': 'operation', 'left': p[1], 'operator': p[2], 'right': p[3]}

def p_term(p):
    '''term : factor
            | term TIMES factor
            | term DIVIDE factor'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = {'type': 'operation', 'left': p[1], 'operator': p[2], 'right': p[3]}

def p_factor(p):
    '''factor : IDENTIFIER
             | NUMBER
             | STRING
             | list
             | function_call
             | LPAREN expression RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]  # For parenthesized expressions

def p_list(p):
    '''list : LBRACKET list_items RBRACKET
           | LBRACKET RBRACKET'''
    if len(p) == 4:
        p[0] = {'type': 'list', 'items': p[2]}
    else:
        p[0] = {'type': 'list', 'items': []}

def p_list_items(p):
    '''list_items : expression
                 | expression COMMA list_items'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_function_call(p):
    '''function_call : IDENTIFIER LPAREN argument_list RPAREN
                    | IDENTIFIER LPAREN RPAREN'''
    if len(p) == 4:
        p[0] = {'type': 'function_call', 'name': p[1], 'arguments': []}
    else:
        p[0] = {'type': 'function_call', 'name': p[1], 'arguments': p[3]}

def p_argument_list(p):
    '''argument_list : expression
                    | expression COMMA argument_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_run_list(p):
    '''run_list : run_statement
                | run_statement run_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_run_statement(p):
    '''run_statement : RUN STRING'''
    p[0] = p[2]

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

# Build the lexer and parser
lexer = lex.lex()
parser = yacc.yacc()

# Test function to parse ThinkPy code
def parse_thinkpy(code):
    return parser.parse(code)

# Example usage
if __name__ == "__main__":
    # Test code with mathematical operations
    test_code = '''
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

    try:
        result = parse_thinkpy(test_code)
        print("Parsed result:", result)
    except Exception as e:
        print("Error parsing code:", str(e))