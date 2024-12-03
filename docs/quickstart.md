# Quickstart Guide

This guide will help you get started with Think quickly. We'll cover basic concepts and write your first Think program.

## Your First Think Program

Here's a simple Think program that calculates student grades:

```python
objective "Calculate student grades"

task "Process Grades":
    step "Get scores":
        scores = [85, 92, 78]

    subtask "Calculate Average":
        total = sum(scores)
        return total / len(scores)
    
    step "Show Results":
        average = Calculate_Average()
        print("Class average:", average)

run "Process Grades"
```

Let's break down each part:

1. `objective`: States what the program aims to accomplish
2. `task`: A major component of your solution
3. `step`: A specific action within a task
4. `subtask`: A reusable computation that returns a value
5. `run`: Executes a task

## Using Think in Jupyter

Think works great in Jupyter notebooks:

```python
%load_ext think.jupyter_magic

%%think --explain
objective "Hello Think"
task "Greeting":
    step "Say Hello":
        message = "Hello, World!"
        print(message)
run "Greeting"
```

The `--explain` flag provides detailed explanations of what's happening.

## Core Concepts

### 1. Problem Decomposition

Think encourages breaking down problems:

```python
objective "Analyze temperature data"

task "Data Collection":
    step "Get readings":
        temps = [72, 75, 68, 70, 73]

task "Analysis":
    subtask "Calculate Average":
        total = sum(temps)
        return total / len(temps)
    
    subtask "Find High":
        return max(temps)

run "Data Collection"
run "Analysis"
```

### 2. Control Flow

Think supports decision-making and loops:

```python
objective "Grade assignments"

task "Process Grades":
    step "Evaluate":
        score = 85
        decide:
            if score >= 90 then:
                grade = "A"
            elif score >= 80 then:
                grade = "B"
            else:
                grade = "C"
        
        # Loop example
        for i in range(3):
            print("Processing assignment", i)
        end

run "Process Grades"
```

### 3. Built-in Functions

Common functions available:
- `print()`: Display output
- `sum()`: Calculate total
- `len()`: Get collection size
- `range()`: Generate number sequence

## Data Types

Think supports these data types:

```python
objective "Demonstrate types"

task "Show Types":
    step "Examples":
        # Numbers
        integer = 42
        float_num = 3.14

        # Strings
        text = "Hello"

        # Lists
        numbers = [1, 2, 3]

        # Dictionaries
        person = {"name": "Alice", "age": 25}

        # Booleans
        flag = True

run "Show Types"
```

## Using Explain Mode

Explain mode helps you understand program execution:

```python
%%think --explain
objective "Understand execution"

task "Example":
    step "Process":
        x = 5
        decide:
            if x > 0 then:
                print("Positive")
            else:
                print("Non-positive")

run "Example"
```

Output includes explanations of each step.

## Next Steps

1. Try more complex examples in the [Tutorials](tutorials/index.html)
2. Learn about best practices in the [User Guide](user_guide/index.html)
3. Explore the [API Reference](api_reference/index.html)
