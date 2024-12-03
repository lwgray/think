import pytest

class TestBasicLexing:
    def test_program_structure_tokens(self, parser):
        code = '''objective "Test"
        task "Hello":
            step "Print":
                x = 42
                print(x)'''
        
        tokens = self._get_tokens(parser, code)
        assert ('OBJECTIVE', 'objective') in tokens
        assert ('STRING', {'type': 'string_literal', 'value': 'Test'}) in tokens
        assert ('TASK', 'task') in tokens
        assert ('STEP', 'step') in tokens
        assert ('NUMBER', 42) in tokens

    def test_control_flow_tokens(self, parser):
        code = '''decide:
            if x > 0 then:
                return True
            elif x < 0 then:
                return False
            else:
                return None'''
        
        tokens = self._get_tokens(parser, code)
        expected = [
            ('DECIDE', 'decide'),
            ('IF', 'if'),
            ('ELIF', 'elif'),
            ('ELSE', 'else'),
            ('THEN', 'then'),
            ('BOOL', 'True'),
            ('BOOL', 'False')
        ]
        assert all(token in tokens for token in expected)

    def test_loop_tokens(self, parser):
        code = '''for i, val in enumerate(numbers):
            print(i)
        for x in range(5):
            print(x)'''
            
        tokens = self._get_tokens(parser, code)
        expected = [
            ('FOR', 'for'),
            ('IN', 'in'),
            ('ENUMERATE', 'enumerate'),
            ('RANGE', 'range'),
            ('NUMBER', 5)
        ]
        assert all(token in tokens for token in expected)

    @staticmethod
    def _get_tokens(parser, code):
        parser.lexer.input(code)
        return [(t.type, t.value) for t in parser.lexer]

class TestNumberLexing:
    def test_integer_tokens(self, parser):
        code = 'x = 42\ny = -17\nz = 0'
        tokens = self._get_tokens(parser, code)
        assert ('NUMBER', 42) in tokens
        assert ('NUMBER', -17) in tokens
        assert ('NUMBER', 0) in tokens

    def test_float_tokens(self, parser):
        code = '''x = 3.14
        y = -0.001
        z = 1.0'''
        tokens = self._get_tokens(parser, code)
        assert ('FLOAT', 3.14) in tokens
        assert ('FLOAT', -0.001) in tokens
        assert ('FLOAT', 1.0) in tokens

    def test_scientific_notation(self, parser):
        code = '''x = 1e5
        y = 1.5e-10
        z = -2.5E+3'''
        tokens = self._get_tokens(parser, code)
        assert ('FLOAT', 1e5) in tokens
        assert ('FLOAT', 1.5e-10) in tokens
        assert ('FLOAT', -2.5e3) in tokens

    @staticmethod
    def _get_tokens(parser, code):
        parser.lexer.input(code)
        return [(t.type, t.value) for t in parser.lexer]

class TestOperatorLexing:
    def test_comparison_tokens(self, parser):
        code = '''x == y
        a != b
        c > d
        e < f
        g >= h
        i <= j'''
        
        tokens = self._get_tokens(parser, code)
        expected = [
            ('EQUALS_EQUALS', '=='),
            ('NOT_EQUALS', '!='),
            ('GREATER', '>'),
            ('LESS', '<'),
            ('GREATER_EQUALS', '>='),
            ('LESS_EQUALS', '<=')
        ]
        assert all(token in tokens for token in expected)

    def test_arithmetic_tokens(self, parser):
        code = 'result = a + b * c / d - e'
        tokens = self._get_tokens(parser, code)
        expected = [
            ('PLUS', '+'),
            ('MINUS', '-'),
            ('TIMES', '*'),
            ('DIVIDE', '/')
        ]
        assert all(token in tokens for token in expected)

    @staticmethod
    def _get_tokens(parser, code):
        parser.lexer.input(code)
        return [(t.type, t.value) for t in parser.lexer]