import pytest


class TestBasicParsing:
    def test_parse_basic_program(self, parser):
        """Test parsing of a simple program with objective, task, and run."""
        code = '''objective "Test"
        task "Hello":
            step "Print":
                print("Hello")
        run "Hello"'''
                
        ast = parser.parse(code)
        assert ast['objective'] == 'Test'
        assert len(ast['tasks']) == 1
        assert ast['tasks'][0]['name'] == 'Hello'
        assert len(ast['runs']) == 1
        assert ast['runs'][0] == 'Hello'

    def test_parse_nested_structures(self, parser):
        """Test parsing of nested data structures."""
        code = '''task "Structures":
            step "Test":
                nested_list = [[1, 2], [3, 4]]
                nested_dict = {"a": {"b": 2}}
                mixed = [{"x": 1}, {"y": 2}]
        run "Structures"'''
        
        ast = parser.parse(code)
        assert len(ast['tasks']) == 1
        step = ast['tasks'][0]['body'][0]
        assert step['name'] == 'Test'
        assert len(step['statements']) == 3

class TestNumberParsing:
    def test_parse_number_literals(self, parser):
        """Test parsing of various number formats."""
        code = '''task "Numbers":
            step "Test":
                regular = 42
                negative = -17
                decimal = 3.14
                scientific = 1.5e-10
                huge = 1e100
                tiny = -2.5e-100
        run "Numbers"'''
        
        ast = parser.parse(code)
        statements = ast['tasks'][0]['body'][0]['statements']
        
        assignments = {s['variable']: s['value'] for s in statements}
        assert assignments['regular'] == 42
        assert assignments['negative'] == -17
        assert assignments['decimal'] == 3.14
        assert assignments['scientific'] == 1.5e-10
        assert assignments['huge'] == 1e100
        assert assignments['tiny'] == -2.5e-100

class TestControlFlow:
    def test_parse_if_elif_else(self, parser):
        """Test parsing of conditional statements."""
        code = '''task "Logic":
            step "Test":
                decide:
                    if x > 0 then:
                        return True
                    elif x == 0 then:
                        return None
                    else:
                        return False'''
                        
        ast = parser.parse(code)
        conditions = ast['tasks'][0]['body'][0]['statements'][0]['conditions']
        assert len(conditions) == 3
        assert conditions[0]['type'] == 'if'
        assert conditions[1]['type'] == 'elif'
        assert conditions[2]['type'] == 'else'

    def test_parse_loops(self, parser):
        """Test parsing of different loop types."""
        code = '''task "Loops":
            step "Test":
                for i in range(5):
                    print(i)
                for idx, val in enumerate(list):
                    print(idx)'''
                    
        ast = parser.parse(code)
        statements = ast['tasks'][0]['body'][0]['statements']
        assert statements[0]['type'] == 'range_loop'
        assert statements[1]['type'] == 'enumerate_loop'

class TestFunctionDefinitions:
    def test_parse_subtask(self, parser):
        """Test parsing of subtask definitions."""
        code = '''task "Functions":
            subtask "calculate":
                x = 1.5e3
                y = -2.718
                return x * y
                
            step "Run":
                result = calculate()
        run "Functions"'''
        
        ast = parser.parse(code)
        task = ast['tasks'][0]
        subtask = next(item for item in task['body'] if item['type'] == 'subtask')
        assert subtask['name'] == 'calculate'
        assert len(subtask['statements']) == 3

class TestErrorHandling:
    @pytest.mark.parametrize("invalid_code", [
        'x = 1.2.3',     # Invalid float
        'x = 1e2e3',     # Invalid scientific notation
        'x = --42',      # Invalid negative number
        'x = 1.e5',      # Invalid float notation
        '''task "Invalid":  # Missing then and colon in if statement
            step "Bad":
                if x > 0
                    print(x)'''
    ])
    def test_parse_errors(self, parser, invalid_code):
        """Test that parser properly handles invalid syntax."""
        with pytest.raises(Exception):
            parser.parse(invalid_code)