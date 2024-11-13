"""
ThinkPy Parser Module

This module implements the parser for the ThinkPy language, handling the conversion
of source code into an Abstract Syntax Tree (AST). It uses PLY (Python Lex-Yacc)
for lexical analysis and parsing.

Key Features:
- Lexical analysis of ThinkPy tokens
- Parsing of program structure (objective, tasks, steps, etc.)
- Support for expressions and control flow
- Comprehensive error handling
"""

import ply.lex as lex
import ply.yacc as yacc
from typing import Any, Dict, List, Optional, Union
import traceback

class ThinkPyParserError(Exception):
    """Custom exception for ThinkPy parsing errors."""
    def __init__(self, message: str, line: int = None, position: int = None, token_value: str = None):
        self.message = message
        self.line = line
        self.position = position
        self.token_value = token_value
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        """Format the error message with line and position information."""
        msg = "ThinkPy Parser Error: " + self.message
        if self.line is not None:
            msg += f" at line {self.line}"
        if self.position is not None:
            msg += f", position {self.position}"
        if self.token_value is not None:
            msg += f" (near '{self.token_value}')"
        return msg

class ThinkPyParser:
    """
    Parser class for ThinkPy language.
    Handles lexical analysis and parsing of ThinkPy code.
    """
    
    tokens = (
        'OBJECTIVE', 'TASK', 'SUBTASK', 'STEP', 'RUN',
        'STRING', 'IDENTIFIER', 'NUMBER', 'EQUALS',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'LBRACKET', 'RBRACKET', 'IF', 'ELSE', 'THEN',
        'DECIDE', 'FOR', 'IN', 'COMMA', 'RETURN',
        'GREATER', 'LESS', 'EQUALS_EQUALS', 'BOOL'
    )

    # Reserved words mapping
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
        'for': 'FOR',
        'in': 'IN',
        'return': 'RETURN',
        'True': 'BOOL',
        'False': 'BOOL'
    }

    # Regular expression rules for simple tokens
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
    t_GREATER = r'>'
    t_LESS = r'<'
    t_EQUALS_EQUALS = r'=='
    
    # Ignored characters (whitespace)
    t_ignore = ' \t\n'

    def __init__(self):
        """Initialize the parser with its lexer and parser instances."""
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self)
        self.source_code = ""

    def t_IDENTIFIER(self, t: lex.LexToken) -> lex.LexToken:
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value, 'IDENTIFIER')
        return t

    def t_STRING(self, t: lex.LexToken) -> lex.LexToken:
        r'"[^"]*"'
        t.value = t.value[1:-1]  # Remove quotes
        return t

    def t_NUMBER(self, t: lex.LexToken) -> lex.LexToken:
        r'-?\d+'
        t.value = int(t.value)
        return t
    
    def t_BOOL(self, t: lex.LexToken) -> lex.LexToken:
        r'True|False'
        t.value = True if t.value == 'True' else False
        return t    

    def t_error(self, t: lex.LexToken):
        """Lexer error handler"""
        raise ThinkPyParserError(
            f"Illegal character '{t.value[0]}'",
            line=self._find_line_number(t.lexpos),
            position=self._find_column_position(t.lexpos)
        )

    def _find_line_number(self, position: int) -> int:
        """Find the line number for a given position in the source code."""
        return self.source_code.count('\n', 0, position) + 1

    def _find_column_position(self, position: int) -> int:
        """Find the column position for a given position in the source code."""
        last_newline = self.source_code.rfind('\n', 0, position)
        if last_newline < 0:
            last_newline = 0
        return position - last_newline

    # Parser rules
    def p_program(self, p):
        """program : objective task_list run_list"""
        p[0] = {'objective': p[1], 'tasks': p[2], 'runs': p[3]}

    def p_objective(self, p):
        """
        objective : OBJECTIVE STRING
        """
        p[0] = p[2]

    def p_task_list(self, p):
        """
        task_list : task
                | task task_list
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]

    def p_task(self, p):
        """
        task : TASK STRING LBRACE step_or_subtask_list RBRACE
        """
        p[0] = {'name': p[2], 'body': p[4]}

    def p_step_or_subtask_list(self, p):
        """
        step_or_subtask_list : step
                            | subtask
                            | step step_or_subtask_list
                            | subtask step_or_subtask_list
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]

    def p_step(self, p):
        """
        step : STEP STRING LBRACE statement_list RBRACE
        """
        p[0] = {'type': 'step', 'name': p[2], 'statements': p[4]}

    def p_subtask(self, p):
        """
        subtask : SUBTASK STRING LBRACE statement_list RBRACE
        """
        p[0] = {'type': 'subtask', 'name': p[2], 'statements': p[4]}

    def p_statement(self, p):
        """
        statement : simple_statement
                | compound_statement
        """
        p[0] = p[1]

    def p_simple_statement(self, p):
        """
        simple_statement : assignment
                        | function_call
                        | return_statement
        """
        p[0] = p[1]

    def p_compound_statement(self, p):
        """
        compound_statement : decide_statement
                        | for_statement
        """
        p[0] = p[1]

    def p_statement_list(self, p):
        """
        statement_list : statement
                    | statement statement_list
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]

    def p_return_statement(self, p):
        """
        return_statement : RETURN expression
        """
        p[0] = {'type': 'return', 'value': p[2]}

    def p_decide_statement(self, p):
        """
        decide_statement : DECIDE LBRACE condition_list RBRACE
        """
        p[0] = {'type': 'decide', 'conditions': p[3]}

    def p_condition_list(self, p):
        """
        condition_list : if_condition
                    | if_condition else_if_list
                    | if_condition else_if_list else_condition
                    | if_condition else_condition
        """
        conditions = [p[1]]  # Start with if condition
        
        if len(p) >= 3:  # Has additional conditions
            if isinstance(p[2], list):  # else if list
                conditions.extend(p[2])
                if len(p) >= 4:  # Has final else
                    conditions.append(p[3])
            else:  # Single else
                conditions.append(p[2])
                
        p[0] = conditions

    def p_else_if_list(self, p):
        """
        else_if_list : else_if_condition
                    | else_if_condition else_if_list
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]

    def p_if_condition(self, p):
        """
        if_condition : IF expression THEN statement_list
        """
        p[0] = {'type': 'if', 'condition': p[2], 'body': p[4]}

    def p_else_if_condition(self, p):
        """
        else_if_condition : ELSE IF expression THEN statement_list
        """
        p[0] = {'type': 'elif', 'condition': p[3], 'body': p[5]}

    def p_else_condition(self, p):
        """
        else_condition : ELSE statement_list
        """
        p[0] = {'type': 'else', 'body': p[2]}

    def p_for_statement(self, p):
        """
        for_statement : FOR IDENTIFIER IN IDENTIFIER LBRACE statement_list RBRACE
        """
        p[0] = {
            'type': 'for_loop',
            'iterator': p[2],
            'iterable': p[4],
            'body': p[6]
        }

    def p_assignment(self, p):
        """
        assignment : IDENTIFIER EQUALS expression
        """
        p[0] = {'type': 'assignment', 'variable': p[1], 'value': p[3]}

    # Add operator precedence rules
    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'GREATER', 'LESS', 'EQUALS_EQUALS'),
    )

    def p_expression(self, p):
        """
        expression : arithmetic_expr
                | comparison_expr
        """
        p[0] = p[1]

    def p_arithmetic_expr(self, p):
        """
        arithmetic_expr : term
                    | arithmetic_expr PLUS term
                    | arithmetic_expr MINUS term
                    | arithmetic_expr TIMES term
                    | arithmetic_expr DIVIDE term
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = {'type': 'operation', 'left': p[1], 'operator': p[2], 'right': p[3]}

    def p_comparison_expr(self, p):
        """
        comparison_expr : arithmetic_expr GREATER arithmetic_expr
                    | arithmetic_expr LESS arithmetic_expr
                    | arithmetic_expr EQUALS_EQUALS arithmetic_expr
        """
        p[0] = {'type': 'operation', 'left': p[1], 'operator': p[2], 'right': p[3]}

    def p_term(self, p):
        """
        term : factor
        """
        p[0] = p[1]

    def p_factor(self, p):
        """
        factor : IDENTIFIER
            | NUMBER
            | STRING
            | BOOL
            | list
            | function_call
            | LPAREN expression RPAREN
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]  # For parenthesized expressions

    def p_list(self, p):
        """
        list : LBRACKET list_items RBRACKET
            | LBRACKET RBRACKET
        """
        if len(p) == 4:
            p[0] = {'type': 'list', 'items': p[2]}
        else:
            p[0] = {'type': 'list', 'items': []}

    def p_list_items(self, p):
        """
        list_items : expression
                | expression COMMA list_items
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_function_call(self, p):
        """
        function_call : IDENTIFIER LPAREN argument_list RPAREN
                    | IDENTIFIER LPAREN RPAREN
        """
        if len(p) == 4:
            p[0] = {'type': 'function_call', 'name': p[1], 'arguments': []}
        else:
            p[0] = {'type': 'function_call', 'name': p[1], 'arguments': p[3]}

    def p_argument_list(self, p):
        """
        argument_list : expression
                    | expression COMMA argument_list
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_run_list(self, p):
        """
        run_list : run_statement
                | run_statement run_list
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]

    def p_run_statement(self, p):
        """
        run_statement : RUN STRING
        """
        p[0] = p[2]


    def p_error(self, p):
        """Parser error handler"""
        if p:
            line_num = self._find_line_number(p.lexpos)
            col_num = self._find_column_position(p.lexpos)
            raise ThinkPyParserError(
                "Syntax error",
                line=line_num,
                position=col_num,
                token_value=p.value
            )
        else:
            raise ThinkPyParserError("Syntax error at end of file")

    def parse(self, code: str) -> Dict[str, Any]:
        """
        Parse ThinkPy code with enhanced error reporting.
        
        Args:
            code: String containing ThinkPy source code
            
        Returns:
            Dict containing the parsed Abstract Syntax Tree
            
        Raises:
            ThinkPyParserError: If parsing fails, with detailed error information
        """
        try:
            self.source_code = code
            return self.parser.parse(code, lexer=self.lexer)
        except ThinkPyParserError:
            raise
        except Exception as e:
            tb = traceback.format_exc()
            raise ThinkPyParserError(f"Parsing failed: {str(e)}\n\nTraceback:\n{tb}")

# Create a global parser instance
_parser = ThinkPyParser()

def parse_thinkpy(code: str) -> Dict[str, Any]:
    """
    Convenience function to parse ThinkPy code using the global parser instance.
    
    Args:
        code: String containing ThinkPy source code
        
    Returns:
        Dict containing the parsed Abstract Syntax Tree
    """
    return _parser.parse(code)

# Example usage
if __name__ == "__main__":
    test_code = '''
    objective "Test conditionals"

    task "Process Order" {
        step "Initialize" {
            order_total = 50
        }
        
        subtask "Verify Payment" {
            decide {
                if order_total > 100 then
                    payment_valid = true
                    requires_approval = true
                else if order_total > 0 then
                    payment_valid = true
                    requires_approval = false
                else
                    payment_valid = false
                    requires_approval = false
            }
            return [payment_valid, requires_approval]
        }
    }

    run "Process Order"
    '''
    
    try:
        result = parse_thinkpy(test_code)
        print("Successfully parsed code!")
        print(result)
    except ThinkPyParserError as e:
        print("\nParsing Error:")
        print(e)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")