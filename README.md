# ThinkPy

ThinkPy is an educational programming language designed to teach computational thinking through problem decomposition. It helps users break down complex problems into manageable parts while providing interactive feedback and explanations.

## Features

- **Structured Problem Solving**: Break down problems into objectives, tasks, subtasks, and steps
- **Interactive Execution**: Run your code and see results in real-time
- **Explain Mode**: Get detailed explanations of what each part of your code does
- **Jupyter Integration**: Use ThinkPy directly in Jupyter notebooks
- **Educational Focus**: Learn computational thinking concepts through hands-on coding

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/thinkpy.git
cd thinkpy

# Install the package
pip install -e .
```

## Quick Start

Here's a simple ThinkPy program that calculates student grades:

```python
objective "Calculate student grades"

task "Data Collection":
    step "Get scores":
        scores = [85, 92, 78, 90, 88]

task "Analysis":
    subtask "Calculate Average":
        total = sum(scores)
        avg = total / len(scores)
        return avg
    
    step "Determine Grade":
        final_score = Calculate_Average()
        decide:
            if final_score >= 90 then:
                grade = "A"
            elif final_score >= 80 then:
                grade = "B"
            else:
                grade = "C"

run "Data Collection"
run "Analysis"
```

## Language Structure

### Core Concepts

1. **Objective**: The main goal of your program
   ```python
   objective "Your goal here"
   ```

2. **Task**: Major components of your solution
   ```python
   task "Task Name":
       # steps or subtasks
   ```

3. **Subtask**: Reusable pieces of code
   ```python
   subtask "Subtask Name":
       # statements
       return result
   ```

4. **Step**: Specific actions
   ```python
   step "Step Name":
       # statements
   ```

### Control Flow

1. **Decide (If/Else)**:
   ```python
    decide:
        if condition then:
           # statements
        elif another_condition then:
           # statements
        else:
           # statements
   ```

2. **Loopd**:
   ```python
    for num in numbers:
       # statements
    end
    for index, value in enumerate(items):
        print(index, value)
    end
    for _, value in enumerate(items):
        print(value)
    end
   ```

### Data Types

- Numbers: `42`, `3.14`
- Strings: `"Hello, World!"`
- Lists: `[1, 2, 3, 4, 5]`
- Variables: `score = 85`
- Dictionaries `{'key': 'value'}

## Jupyter Notebook Usage

1. Load the ThinkPy extension:
   ```python
   %load_ext thinkpy.jupyter_magic
   ```

2. Write ThinkPy code in cells:
   ```python
   %%thinkpy --explain
   
   objective "Your program objective"
   # ... rest of your code
   ```

## Built-in Functions

- `sum(list)`: Calculate the sum of a list
- `len(list)`: Get the length of a list
- `print(value)`: Display a value

## Examples

### Temperature Analysis
```python
objective "Analyze temperature data"

task "Data Collection":
    step "Get readings":
        temps = [72, 75, 68, 70, 73]

task "Analysis":
    subtask "Calculate Average":
        total = sum(temps)
        avg = total / len(temps)
        return avg
    
    subtask "Find High":
        max_temp = temps[0]
        for index, value in enumerate(temps):
            decide:
                if temps[index] > max_temp then:
                    max_temp = temps[index]
        end
        return max_temp

run "Data Collection"
run "Analysis"
```

### Grade Calculator
```python
objective "Calculate final grades"

task "Setup":
    step "Initialize data":
        scores = [85, 92, 78]
        weights = [0.3, 0.4, 0.3]

task "Calculate":
    subtask "Weighted Average":
        total = 0
        for index in range(3):
            total = total + (scores[index] * weights[index])
        end
        return total

run "Setup"
run "Calculate"
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors to this project
- Inspired by Python and educational programming concepts
- Built with PLY (Python Lex-Yacc)

## Support

For support, feature requests, or bug reports:
1. Check the [documentation](https://thinkpy.readthedocs.io/)
2. Open an issue on GitHub
3. Contact the maintainers

---

Made with ❤️ for teaching computational thinking