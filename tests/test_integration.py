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

        print(f"\n>>> Debug: Captured output:\n{output}")  # More visible debug output

        output_lines = output.strip().split('\n')
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
    def test_conditional_execution(self, interpreter, parser, capture_output):
        code = '''objective "Test conditional execution"
        task "Logic":
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
        code = '''objective "Test loop execution"
        task "Loop":
            step "Iterate":
                numbers = [1, 2, 3]
                for num in numbers:
                    print(num)
                end
        run "Loop"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        output = capture_output.getvalue()
        assert all(str(n) in output for n in [1, 2, 3])

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
        print(interpreter.state)
        #assert interpreter.state['items'][0] == 0
        #assert interpreter.state['items'][2] == 2
        assert False

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
                for n in numbers:
                    decide:
                        if n > 3 then:
                            print(n)
                end
        run "Process"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        output = capture_output.getvalue()
        four = output.strip().split('\n')[-2].split()[-1]
        five = output.strip().split('\n')[-1].split()[-1]
        assert 4 == int(four)
        assert 5 == int(five)