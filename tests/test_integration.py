import pytest
import io
import sys
from think.interpreter import ThinkInterpreter
from think.errors import ThinkRuntimeError

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

    def test_list_indexing(self, interpreter, parser, capture_output):
        """Test comprehensive list indexing operations."""
        code = '''objective "Test list indexing"
        task "ListIndexing":
            step "Setup":
                numbers = [10, 20, 30, 40, 50]
                
                first = numbers[0]
                last = numbers[4]
                
                last_item = numbers[-1]
                second_to_last = numbers[-2]
                
                idx = 2
                middle = numbers[idx]
                
                expr_idx = numbers[1 + 1]
                
                matrix = [[1, 2, 3], [4, 5, 6]]
                nested_val = matrix[1][2]
                
                calc_idx = 10 / 2 - 1
                computed = numbers[calc_idx]
                
        run "ListIndexing"'''
    
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        # Verify basic positive indexing
        assert interpreter.state['first'] == 10, "First element incorrect"
        assert interpreter.state['last'] == 50, "Last element incorrect"
        
        # Verify negative indexing
        assert interpreter.state['last_item'] == 50, "Negative indexing failed"
        assert interpreter.state['second_to_last'] == 40, "Negative indexing failed"
        
        # Verify variable as index
        assert interpreter.state['middle'] == 30, "Variable index failed"
        
        # Verify expression as index
        assert interpreter.state['expr_idx'] == 30, "Expression index failed"
        
        # Verify nested indexing
        assert interpreter.state['nested_val'] == 6, "Nested indexing failed"
        
        # Verify computed index
        assert interpreter.state['computed'] == 50, "Computed index failed"

    def test_list_indexing_errors(self, interpreter, parser, capture_output):
        """Test error cases for list indexing."""
        # Test index out of bounds (positive)
        code = '''objective "Test list index errors"
        task "ListErrors":
            step "OutOfBounds":
                numbers = [1, 2, 3]
                invalid = numbers[5]
        run "ListErrors"'''
        
        with pytest.raises(ThinkRuntimeError) as exc_info:
            ast = parser.parse(code)
            interpreter.execute(ast)
        assert "Invalid index/key" in str(exc_info.value)
        
        # Test index out of bounds (negative)
        code = '''objective "Test negative index errors"
        task "ListErrors":
            step "NegativeOutOfBounds":
                numbers = [1, 2, 3]
                invalid = numbers[-4]
        run "ListErrors"'''
        
        with pytest.raises(ThinkRuntimeError) as exc_info:
            ast = parser.parse(code)
            interpreter.execute(ast)
        assert "Invalid index/key" in str(exc_info.value)
        
        # Test non-integer index
        code = '''objective "Test non-integer index"
        task "ListErrors":
            step "NonInteger":
                numbers = [1, 2, 3]
                invalid = numbers[1.5]
        run "ListErrors"'''
        
        with pytest.raises(ThinkRuntimeError) as exc_info:
            ast = parser.parse(code)
            interpreter.execute(ast)
        assert "Invalid index/key" in str(exc_info.value)
        
        # Test invalid type for index
        code = '''objective "Test invalid index type"
        task "ListErrors":
            step "InvalidType":
                numbers = [1, 2, 3]
                invalid = numbers["one"]
        run "ListErrors"'''
        
        with pytest.raises(ThinkRuntimeError) as exc_info:
            ast = parser.parse(code)
            interpreter.execute(ast)
        assert "Invalid index/key" in str(exc_info.value)

    def test_nested_list_indexing_errors(self, interpreter, parser, capture_output):
        """Test error cases for nested list indexing."""
        # Test accessing index of non-list
        code = '''objective "Test invalid nested indexing"
        task "NestedErrors":
            step "NonList":
                numbers = [1, [2, 3], 4]
                invalid = numbers[0][1]
        run "NestedErrors"'''
        
        with pytest.raises(ThinkRuntimeError) as exc_info:
            ast = parser.parse(code)
            interpreter.execute(ast)
        assert "Cannot index into type" in str(exc_info.value)
        
        # Test out of bounds on nested list
        code = '''objective "Test nested out of bounds"
        task "NestedErrors":
            step "OutOfBounds":
                matrix = [[1, 2], [3, 4]]
                invalid = matrix[1][5]
        run "NestedErrors"'''
        
        with pytest.raises(ThinkRuntimeError) as exc_info:
            ast = parser.parse(code)
            interpreter.execute(ast)
        assert "Invalid index" in str(exc_info.value)
        

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

    def test_basic_index_addition(self, interpreter, parser,capture_output):
        """Test that operations can be performed on indexed variables"""
        code = '''
        objective "Test basic index operations"
        task "operation":
            step "add":
                mylist = [1,2,3]
                result = mylist[0] + mylist[1]
        run "operation"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)

        assert interpreter.state['result'] == 3

    def test_indexed_arithmetic_operations(self, interpreter, parser, capture_output):
        """Test arithmetic operations with indexed values."""
        code = '''
        objective "Test indexed arithmetic"
        task "IndexedMath":
            step "Calculate":
                list1 = [10, 20, 30]
                list2 = [2, 4, 6]
                list3 = [1, 2, 3]
                
                add_result = list1[0] + list2[1]
                
                mixed_result = list1[1] * list2[0] + list3[2]
                
                complex_result = (list1[2] + list2[1]) * list3[0]
                
                i = 1
                var_index_result = list1[i] + list2[i]
                
                nested_calc = (list1[0] * list2[1]) + (list3[2] / list2[0])
                
        run "IndexedMath"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        # 10 + 4 = 14
        assert interpreter.state['add_result'] == 14
        
        # 20 * 2 + 3 = 43
        assert interpreter.state['mixed_result'] == 43
        
        # (30 + 4) * 1 = 34
        assert interpreter.state['complex_result'] == 34
        
        # list1[1] + list2[1] = 20 + 4 = 24
        assert interpreter.state['var_index_result'] == 24
        
        # (10 * 4) + (3 / 2) = 40 + 1.5 = 41.5
        assert pytest.approx(interpreter.state['nested_calc']) == 41.5

    def test_nested_indexed_operations(self, interpreter, parser, capture_output):
        """Test operations with nested indexed values and complex expressions."""
        code = '''
        objective "Test nested indexed operations"
        task "NestedIndex":
            step "Calculate":
                matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
                multipliers = [2, 3, 4]
                
                nested_result = matrix[1][2] * multipliers[0]
                
                i = 1
                j = 2
                complex_nested = matrix[i][j] + matrix[0][j] * multipliers[i]
                
        run "NestedIndex"'''
        
        ast = parser.parse(code)
        interpreter.execute(ast)
        
        # matrix[1][2] * multipliers[0] = 6 * 2 = 12
        assert interpreter.state['nested_result'] == 12
        
        # matrix[1][2] + matrix[0][2] * multipliers[1] = 6 + 3 * 3 = 15
        assert interpreter.state['complex_nested'] == 15

    def test_indexed_operation_errors(self, interpreter, parser, capture_output):
        """Test error handling in indexed operations."""
        # Test invalid index in operation
        code = '''
        objective "Test invalid index in operation"
        task "InvalidIndex":
            step "Calculate":
                numbers = [1, 2, 3]
                result = numbers[3] + numbers[1]
        run "InvalidIndex"'''
        
        with pytest.raises(ThinkRuntimeError) as exc_info:
            ast = parser.parse(code)
            interpreter.execute(ast)
        assert "Invalid index/key" in str(exc_info.value)
        
        # Test operation with invalid nested index
        code = '''
        objective "Test invalid nested index"
        task "InvalidNested":
            step "Calculate":
                matrix = [[1, 2], [3, 4]]
                result = matrix[1][5] * 2
        run "InvalidNested"'''
        
        with pytest.raises(ThinkRuntimeError) as exc_info:
            ast = parser.parse(code)
            interpreter.execute(ast)
        assert "Invalid index/key" in str(exc_info.value)
