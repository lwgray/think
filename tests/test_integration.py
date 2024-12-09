import pytest
import io
import sys
from think.interpreter import ThinkInterpreter

@pytest.fixture
def capture_output():
    """Fixture to capture stdout and restore it after test."""
    import sys
    from io import StringIO
    
    # Store the original stdout
    old_stdout = sys.stdout
    
    # Create our string buffer
    string_buffer = StringIO()
    
    try:
        # Replace stdout
        sys.stdout = string_buffer
        yield string_buffer
    finally:
        # Restore stdout
        sys.stdout = old_stdout
        string_buffer.close()

class TestBasicIntegration:
    def test_arithmetic_operations(self, interpreter, parser, capture_output):
        code = '''
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
        run "Math"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        output = capture_output.getvalue()

        output_lines = output.strip().split('\n')
        print(output_lines)
        int_result = interpreter.state['int_result']
        float_result = interpreter.state['float_result']
        sci_result = interpreter.state['sci_result']
        mixed_result = interpreter.state['mixed']
        assert int_result == 25
        assert pytest.approx(float_result) == -7.85
        assert pytest.approx(float(sci_result)) == 15.0
        assert pytest.approx(float(mixed_result)) == -131.94678

    def test_scientific_notation(self, interpreter, parser, capture_output):
        code = '''objective "Test"
            task "Scientific":
            step "Complex Math":
                tiny = 1.5e-10
                huge = 2.0e5
                result = huge * tiny
                print(result)
        run "Scientific"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        result = interpreter.state['result']
        assert any(x == result for x in [3e-05, 0.00003])

class TestControlFlow:
    def test_conditional_execution(self, capture_output, interpreter, parser):        
        code = '''objective "Test conditional execution"
            task "Logic":
                step "Test":
                    x = 5
                    decide:
                        if x > 0 then:
                            result = "positive"
                            print(result)
                        elif x == 0 then:
                            result = "zero"
                            print(result)
                        else:
                            result = "negative"
                            print(result)
            run "Logic"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        output = capture_output.getvalue()
        assert interpreter.state['result'] == "positive"

    def test_loop_execution(self, interpreter, parser, capture_output):
        code = '''objective "Test loop execution"
        task "Loop":
            step "Iterate":
                numbers = [1, 2, 3]
                for num in numbers:
                    result = num
                end
        run "Loop"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        assert interpreter.state['result'] == 3

class TestDataStructures:
    def test_nested_structures(self, interpreter, parser, capture_output):
        code = '''objective "Test nested structures"
        task "Data":
            step "Test":
                users = [
                    {"name": "Alice", "scores": [90, 85]},
                    {"name": "Bob", "scores": [88, 92]}
                ]
                print(users[0]["name"])
                print(users[1]["scores"][1])
        run "Data"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        assert interpreter.state['users'][0]['name'] == "Alice"
        assert interpreter.state['users'][1]['scores'][1] == 92

    def test_list_operations(self, interpreter, parser, capture_output):
        code = '''objective "Test list operations"
        task "Lists":
            step "Process":
                items = []
                for i in range(3):
                    items = items + [i]
                end
                print(items[0])
                print(items[2])
        run "Lists"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        assert interpreter.state['items'][0] == 0
        assert interpreter.state['items'][2] == 2
        

class TestFunctions:
    def test_subtask_execution(self, interpreter, parser, capture_output):
        code = '''objective "Test subtask execution"
        task "Functions":
            subtask "calculate":
                x = 5
                return x * 2
                
            subtask "process":
                base = calculate()
                return base + 3
                
            step "Run":
                result = process()
                print(result)
        run "Functions"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        assert 13 == interpreter.state['result']

    def test_data_processing(self, interpreter, parser, capture_output):
        code = '''objective "Test data processing"
        task "Process":
            step "Filter":
                numbers = [1, 2, 3, 4, 5]
                result = []
                for n in numbers:
                    decide:
                        if n > 3 then:
                            result = result + [n]
                end
        run "Process"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)

        assert 4 == interpreter.state['result'][0]
        assert 5 == interpreter.state['result'][1]

class TestExpressionEvaluation:
    def test_nested_unary_operations(self, interpreter, parser, capture_output):
        """Test handling of nested unary minus operations."""
        code = '''
        objective "Test nested unary operations"
        task "UnaryOps":
            step "Calculate":
                double_neg = - -42
                triple_neg = - - -17
                mixed = - -3.14
                print(double_neg)
                print(triple_neg)
                print(mixed)
        run "UnaryOps"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        assert interpreter.state['double_neg'] == 42
        assert interpreter.state['triple_neg'] == -17
        assert pytest.approx(interpreter.state['mixed']) == 3.14

    def test_complex_nested_expressions(self, interpreter, parser, capture_output):
        """Test evaluation of complex nested expressions."""
        code = '''
        objective "Test complex expressions"
        task "ComplexExpr":
            step "Calculate":
                a = 5
                b = 3
                c = 8
                d = 2
                nested1 = (a + b) * (c - d)
                nested2 = ((a * b) + c) / (d + 1)
                print(nested1)
                print(nested2)
        run "ComplexExpr"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        # (5 + 3) * (8 - 2) = 8 * 6 = 48
        assert interpreter.state['nested1'] == 48
        # ((5 * 3) + 8) / (2 + 1) = (15 + 8) / 3 = 23/3
        assert pytest.approx(interpreter.state['nested2']) == 7.666666666666667

    def test_parenthesized_expressions(self, interpreter, parser, capture_output):
        """Test evaluation of expressions with explicit parentheses."""
        code = '''
        objective "Test parenthesized expressions"
        task "ParenExpr":
            step "Calculate":
                simple = 2 * (3 + 4)
                complex = (1 + 2) * (3 - 4) / (5 + 6)
                nested = (((1 + 2) * 3) - 4)
                print(simple)
                print(complex)
                print(nested)
        run "ParenExpr"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        # 2 * (3 + 4) = 2 * 7 = 14
        assert interpreter.state['simple'] == 14
        # (1 + 2) * (3 - 4) / (5 + 6) = 3 * (-1) / 11 ≈ -0.2727
        assert pytest.approx(interpreter.state['complex']) == -0.2727272727272727
        # (((1 + 2) * 3) - 4) = ((3 * 3) - 4) = (9 - 4) = 5
        assert interpreter.state['nested'] == 5

    def test_operator_precedence(self, interpreter, parser, capture_output):
        """Test proper handling of operator precedence."""
        code = '''
        objective "Test operator precedence"
        task "Precedence":
            step "Calculate":
                mul_add = 2 + 3 * 4
                div_add = 10 + 15 / 3
                mixed = 2 * 3 + 4 * 5 / 2 - 1
                print(mul_add)
                print(div_add)
                print(mixed)
        run "Precedence"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        # 2 + 3 * 4 = 2 + 12 = 14 (not 20)
        assert interpreter.state['mul_add'] == 14
        # 10 + 15 / 3 = 10 + 5 = 15 (not 8.33...)
        assert interpreter.state['div_add'] == 15
        # 2 * 3 + 4 * 5 / 2 - 1 = 6 + 20/2 - 1 = 6 + 10 - 1 = 15
        assert interpreter.state['mixed'] == 15

    def test_basic_parentheses(self, interpreter, parser, capture_output):
        """Test basic parenthesized expression."""
        code = '''
        objective "Test basic parentheses"
        task "ParenExpr":
            step "Calculate":
                result = 2 * (3 + 4)
                print(result)
        run "ParenExpr"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        assert interpreter.state['result'] == 14