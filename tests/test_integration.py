import pytest
import io
import sys

@pytest.fixture
def capture_output():
    """Fixture to capture stdout and restore it after test."""
    captured_output = io.StringIO()
    sys.stdout = captured_output
    yield captured_output
    sys.stdout = sys.__stdout__

class TestBasicIntegration:
    def test_arithmetic_operations(self, interpreter, parser, capture_output):
        code = '''objective "Test"
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
        assert '25' in output
        assert '-7.85' in output
        assert '15.0' in output
        assert '-131.94678' in output

    def test_scientific_notation(self, interpreter, parser, capture_output):
        code = '''task "Scientific":
            step "Complex Math":
                tiny = 1.5e-10
                huge = 2.0e5
                result = huge * tiny
                print(result)
        run "Scientific"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        output = capture_output.getvalue()
        assert any(x in output for x in ['3e-05', '0.00003'])

class TestControlFlow:
    def test_conditional_execution(self, interpreter, parser, capture_output):
        code = '''task "Logic":
            step "Test":
                x = 5
                decide:
                    if x > 0 then:
                        print("positive")
                    elif x == 0 then:
                        print("zero")
                    else:
                        print("negative")
        run "Logic"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        assert "positive" in capture_output.getvalue()

    def test_loop_execution(self, interpreter, parser, capture_output):
        code = '''task "Loop":
            step "Iterate":
                numbers = [1, 2, 3]
                for num in numbers:
                    print(num)
        run "Loop"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        output = capture_output.getvalue()
        assert all(str(n) in output for n in [1, 2, 3])

class TestDataStructures:
    def test_nested_structures(self, interpreter, parser, capture_output):
        code = '''task "Data":
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
        
        output = capture_output.getvalue()
        assert "Alice" in output
        assert "92" in output

    def test_list_operations(self, interpreter, parser, capture_output):
        code = '''task "Lists":
            step "Process":
                items = []
                for i in range(3):
                    items = items + [i]
                print(items[0])
                print(items[2])
        run "Lists"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        output = capture_output.getvalue()
        assert "0" in output
        assert "2" in output

class TestFunctions:
    def test_subtask_execution(self, interpreter, parser, capture_output):
        code = '''task "Functions":
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
        assert "13" in capture_output.getvalue()

    def test_data_processing(self, interpreter, parser, capture_output):
        code = '''task "Process":
            step "Filter":
                numbers = [1, 2, 3, 4, 5]
                for n in numbers:
                    decide:
                        if n > 3 then:
                            print(n)
        run "Process"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        output = capture_output.getvalue()
        assert "4" in output
        assert "5" in output