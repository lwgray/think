"""
Think Parser Module

This module implements the parser for the Think language, handling the conversion
of source code into an Abstract Syntax Tree (AST). It uses PLY (Python Lex-Yacc)
for lexical analysis and parsing.

Key Features:
- Lexical analysis of Think tokens
- Parsing of program structure (objective, tasks, steps, etc.)
- Support for expressions and control flow
- Comprehensive error handling
"""

import ply.lex as lex
import ply.yacc as yacc
from typing import Any
import traceback
try:
    from .errors import ThinkParserError, ThinkError
    from .validator import ThinkValidator
except ImportError:
    from errors import ThinkParserError, ThinkError
    from validator import ThinkValidator



class ThinkParser:
    """
    Parser class for Think language.
    Handles lexical analysis and parsing of Think code.
    """
    
    tokens = (
        'OBJECTIVE', 'TASK', 'SUBTASK', 'STEP', 'RUN',
        'STRING', 'IDENTIFIER', 'NUMBER', 'EQUALS',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'LBRACKET', 'RBRACKET', 'IF', 'ELSE', 'THEN',
        'DECIDE', 'FOR', 'IN', 'COMMA', 'RETURN',
        'GREATER', 'LESS', 'EQUALS_EQUALS', 'BOOL',
        'ELIF', 'FLOAT', 'GREATER_EQUALS', 'LESS_EQUALS',
        'NOT_EQUALS', 'COLON', 'UNDERSCORE', 'RANGE',
        'ENUMERATE', 'NEWLINE', 'END'
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
        'False': 'BOOL',
        'elif': 'ELIF',
        'range': 'RANGE',
        'enumerate': 'ENUMERATE',
        'end': 'END'
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
    t_GREATER_EQUALS = r'>='
    t_LESS_EQUALS = r'<='
    t_NOT_EQUALS = r'!='
    t_COLON = r':'
    t_UNDERSCORE = r'_'
    
    # Ignored characters (whitespace)
    t_ignore = ' \t\n'

    def __init__(self):
        """Initialize the parser with its lexer and parser instances."""
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self)
        self.source_code = ""

    def t_IDENTIFIER(self, t: lex.LexToken) -> lex.LexToken:
        r"""[a-zA-Z_][a-zA-Z0-9_]*"""
        t.type = self.reserved.get(t.value, 'IDENTIFIER')
        return t

    def t_STRING(self, t: lex.LexToken) -> lex.LexToken:
        r"""(\"[^\"]*\")|(\'[^\']*\')|(\"{3}[^\"]*\"{3})|(\'{3}[^\']*\'{3})"""
        # Remove outer quotes while preserving inner content
        if t.value.startswith('"""') or t.value.startswith("'''"):
            t.value = {'type': 'string_literal', 'value': t.value[3:-3]}
        else:
            t.value = {'type': 'string_literal', 'value': t.value[1:-1]}
        return t

    def t_FLOAT(self, t: lex.LexToken) -> lex.LexToken:
        r"""-?\d*\.\d+([eE][-+]?\d+)?|-?\d+[eE][-+]?\d+"""
        t.value = float(t.value)
        return t 
    
    def t_NUMBER(self, t: lex.LexToken) -> lex.LexToken:
        r"""-?\d+"""
        t.value = int(t.value)
        return t
    
    def t_BOOL(self, t: lex.LexToken) -> lex.LexToken:
        r"""True|False"""
        t.value = True if t.value == 'True' else False
        return t
    
    def t_NEWLINE(self, t: lex.LexToken) -> lex.LexToken:
        r"""\n+"""
        t.lexer.lineno += len(t.value)
        return t

    def t_error(self, t: lex.LexToken):
        """Lexer error handler"""
        print(f"DEBUG: Error at token: {t.value[0]}")
        print(f"DEBUG: Position: {t.lexpos}")
        print(f"DEBUG: Remaining input: {t.value[:20]}")
        line_num = self._find_line_number(t.lexpos)
        col_num = self._find_column_position(t.lexpos)
        raise ThinkParserError(
            f"Illegal character '{t.value[0]}'",
            line=line_num,
            column=col_num
        )
    
    def t_debug(self, t: lex.LexToken):
        """Debug token stream"""
        print(f"DEBUG: Token: {t.type}, Value: {t.value}, pos={t.lexpos}")
        return t

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
        obj_value = p[2]['value'] if isinstance(p[2], dict) and p[2].get('type') == 'string_literal' else p[2]
        p[0] = obj_value

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
        task : TASK STRING COLON step_or_subtask_list
        """
        task_name = p[2]['value'] if isinstance(p[2], dict) and p[2].get('type') == 'string_literal' else p[2]
        p[0] = {'name': task_name, 'body': p[4]}

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
        step : STEP STRING COLON statement_list
        """
        step_name = p[2]['value'] if isinstance(p[2], dict) and p[2].get('type') == 'string_literal' else p[2]
        p[0] = {'type': 'step', 'name': step_name, 'statements': p[4]}

    def p_subtask(self, p):
        """
        subtask : SUBTASK STRING COLON statement_list
        """
        subtask_name = p[2]['value'] if isinstance(p[2], dict) and p[2].get('type') == 'string_literal' else p[2]
        p[0] = {'type': 'subtask', 'name': subtask_name, 'statements': p[4]}

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
                    | empty
        """
        if len(p) == 2:
            if p[1] is None:  # empty case
                p[0] = []
            else:  # single statement
                p[0] = [p[1]]
        else:  # statement followed by more statements
            if isinstance(p[2], list):
                p[0] = [p[1]] + p[2]
            else:
                p[0] = [p[1], p[2]]

    def p_return_statement(self, p):
        """
        return_statement : RETURN expression
        """
        p[0] = {'type': 'return', 'value': p[2]}

    def p_empty(self, p):
        """
        empty :
        """
        p[0] = None

    def p_decide_statement(self, p):
        """
        decide_statement : DECIDE COLON condition_list 
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
        
        if len(p) == 3:  # Has one additional condition
            if isinstance(p[2], list):  # else if list
                conditions.extend(p[2])
            else:  # else condition
                conditions.append(p[2])
        elif len(p) == 4:  # Has else-if list and else
            conditions.extend(p[2])
            conditions.append(p[3])
        
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
        if_condition : IF expression THEN COLON statement_list 
        """
        p[0] = {
            'type': 'if', 
            'condition': p[2], 
            'body': p[5]
        }

    def p_else_if_condition(self, p):
        """
        else_if_condition : ELIF expression THEN COLON statement_list
        """
        p[0] = {
            'type': 'elif',
            'condition': p[2],
            'body': p[5]
        }

    def p_else_condition(self, p):
        """
        else_condition : ELSE COLON statement_list
        """
        if len(p) == 5:  # With statements
            p[0] = {
                'type': 'else',
                'body': p[3] if isinstance(p[3], list) else [p[3]]
            }
        else:  # Empty block
            p[0] = {
                'type': 'else',
                'body': []
            }

    def p_for_statement(self, p):
        """
        for_statement : FOR IDENTIFIER IN iterable COLON loop_body END
                    | FOR IDENTIFIER COMMA IDENTIFIER IN ENUMERATE LPAREN IDENTIFIER RPAREN COLON loop_body END
                    | FOR UNDERSCORE COMMA IDENTIFIER IN ENUMERATE LPAREN IDENTIFIER RPAREN COLON loop_body END
                    | FOR IDENTIFIER IN RANGE LPAREN expression RPAREN COLON loop_body END
        """      
        if len(p) == 13:
            p[0] = {
                'type': 'enumerate_loop',
                'index': p[2],
                'element': p[4],
                'iterable': p[8],
                'body': p[11]
            }
        
        elif len(p) == 11: # Range loop
            p[0] = {
                'type': 'range_loop',
                'iterator': p[2],
                'range': p[6],
                'body': p[9]    
            }

        else:
            p[0] = {
                'type': 'for_loop',
                'iterator': p[2],
                'iterable': p[4],
                'body': p[6]
            }
        

    def p_loop_body(self, p):
        """
        loop_body : statement
                | statement loop_body
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]

    def p_iterable(self, p):
        """
        iterable : IDENTIFIER
                | RANGE LPAREN expression RPAREN
                | ENUMERATE LPAREN IDENTIFIER RPAREN
        """
        if len(p) == 2:  # Simple identifier
            p[0] = p[1]
        elif len(p) == 5:  # range() or enumerate()
            if p[1] == 'range':
                p[0] = {'type': 'range', 'end': p[3]}
            else:  # enumerate
                p[0] = {'type': 'enumerate', 'iterable': p[3]}


    def p_indexing(self, p):
        '''expression : expression LBRACKET expression RBRACKET'''
        p[0] = {
            'type': 'index',
            'container': p[1],
            'key': p[3]
        }

    def p_assignment(self, p):
        """
        assignment : IDENTIFIER EQUALS expression
        """
        p[0] = {'type': 'assignment', 'variable': p[1], 'value': p[3]}

    # Add operator precedence rules
    precedence = (
        ('right', 'UMINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'GREATER', 'LESS', 'GREATER_EQUALS', 'LESS_EQUALS'),
        ('EQUALS_EQUALS', 'NOT_EQUALS')
    )

    def p_expression(self, p):
        """
        expression : arithmetic_expr
                | comparison_expr
                | dict_literal
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
                    | arithmetic_expr GREATER_EQUALS arithmetic_expr
                    | arithmetic_expr LESS_EQUALS arithmetic_expr
                    | arithmetic_expr NOT_EQUALS arithmetic_expr
        """
        p[0] = {'type': 'operation', 'left': p[1], 'operator': p[2], 'right': p[3]}

    def p_term(self, p):
        """
        term : factor
        """
        p[0] = p[1]

    def p_factor_unary(self, p):
        """
        factor : MINUS factor %prec UMINUS
        """
        if isinstance(p[2], (int, float)):
            p[0] = -p[2]
        else:
            p[0] = {'type': 'operation',
                    'operator': '*',
                    'left': -1,
                    'right': p[2]}

    def p_factor(self, p):
        """
        factor : IDENTIFIER
            | NUMBER
            | numeric_literal
            | STRING
            | BOOL
            | FLOAT
            | MINUS FLOAT
            | list
            | function_call
            | LPAREN expression RPAREN
            | dict_literal
            | index_expression
        """
        if len(p) == 2:
            if isinstance(p[1], str) and hasattr(p[1], 'type'):
                p[0] = p[1]
            elif p.slice[1].type == 'STRING':
                p[0] = {'type': 'string_literal', 'value': p[1]}
            else:
                p[0] = p[1]
        elif len(p) == 3 and p[1] == '-':
            p[0] = -p[2]
        else:
            p[0] = p[2]  # For parenthesized expressions

    def p_numeric_literal(self, p):
        """
        numeric_literal : NUMBER
                    | FLOAT
                    | MINUS NUMBER
                    | MINUS FLOAT
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = -p[2]

    def p_dict_literal(self, p):
        """
        dict_literal : LBRACE dict_entries RBRACE
            | LBRACE RBRACE
        """
        if len(p) == 3:
            p[0] = {'type': 'dict', 'entries': []}
        else:
            p[0] = {'type': 'dict', 'entries': p[2]}

    def p_dict_entries(self, p):
        """
        dict_entries : dict_entry
            | dict_entry COMMA dict_entries
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_dict_entry(self, p):
        """
        dict_entry : expression COLON expression
        """
        p[0] = {'key': p[1], 'value': p[3]}

    def p_index_expression(self, p):
        """
        index_expression : expression LBRACKET expression RBRACKET
        """
        p[0] = {
            'type': 'index', 
            'container': p[1], 
            'key': p[3]
            }    
    
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
        run_name = p[2]['value'] if isinstance(p[2], dict) and p[2].get('type') == 'string_literal' else p[2]
        p[0] = run_name

    def p_error(self, p):
        """Enhanced parser error handler"""
        if p:
            print(f"DEBUG: Syntax error at token type: {p.type}")
            print(f"DEBUG: Token value: {p.value}")
            print(f"DEBUG: Position: {p.lexpos}")
            line_num = self._find_line_number(p.lexpos)
            col_num = self._find_column_position(p.lexpos)
            source_context = self.get_source_context(p.lexpos)
            
            raise ThinkParserError(
                message=f"Syntax error at token {p.type}",
                line=line_num,
                column=col_num,
                token=p.value,
                source_snippet=source_context
            )
        
    def get_source_context(self, position, window=2):
        """Get source code context around an error position"""
        lines = self.source_code.split('\n')
        line_num = self._find_line_number(position)
        
        start = max(0, line_num - window - 1)
        end = min(len(lines), line_num + window)
        
        context_lines = []
        for i in range(start, end):
            prefix = '-> ' if i == line_num - 1 else '   '
            context_lines.append(f"{prefix}{i+1}: {lines[i]}")
        
        return '\n'.join(context_lines)

    def parse(self, code: str) -> dict[str, Any]:
        """
        Parse Think code with enhanced error reporting.
        
        Args:
            code: String containing Think source code
            
        Returns:
            Dict containing the parsed Abstract Syntax Tree
            
        Raises:
            ThinkParserError: If parsing fails, with detailed error information
        """
        try:
            self.source_code = code
            ast = self.parser.parse(code, lexer=self.lexer)

            # Validate the parsed AST
            validator = ThinkValidator()
            validator.validate_program(ast, code)
            return ast
        except ThinkParserError as e:
            if not e.context:
                validator = ThinkValidator()
                e.context = validator.get_context_lines(e.line if e.line else 1)
            raise
        except Exception as e:
            if isinstance(e, ThinkError):
                raise
            line_num = 1
            raise ThinkParserError(
                message=str(e),
                line=line_num,
                column=1,
                token="",
                source_snippet=ThinkValidator()._get_context_lines(line_num)
            )

# Create a global parser instance
_parser = ThinkParser()

def parse_think(code: str) -> dict[str, Any]:
    """
    Convenience function to parse Think code using the global parser instance.
    
    Args:
        code: String containing Think source code
        
    Returns:
        Dict containing the parsed Abstract Syntax Tree
    """
    return _parser.parse(code)

# Example usage
if __name__ == "__main__":
    pass