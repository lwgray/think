====================================
PEP 1 - Think Language Style Guide
====================================

Introduction
------------

This document provides style guidelines for the Think programming language. Think emphasizes readability and clear expression of problem decomposition. This guide aims to help programmers write code that is consistent and maintainable.

Program Structure
-----------------

Objectives
^^^^^^^^^^

Each program must begin with a single, clear objective that defines its purpose. The objective should be concise but descriptive:

.. code-block:: python

    # Good
    objective "Calculate student grades and generate report"

    # Bad - Too vague
    objective "Process data"

    # Bad - Multiple purposes
    objective "Calculate grades and manage attendance and track assignments"

Tasks
^^^^^

Tasks represent major components of your solution. Each task should have a clear, specific purpose.

**Naming Conventions:**

- Use clear, descriptive names
- Names should be action-oriented
- Be specific about purpose
- Use natural language phrasing

.. code-block:: python

    # Good
    task "Process Grades":
        step "Initialize":
            grades = [85, 92, 78]

    # Bad - too vague
    task "Do Stuff":
        step "Setup":
            x = [85, 92, 78]

**Organization:**

- Group related tasks together
- Each task should have a single responsibility
- Order tasks logically based on data flow

.. code-block:: python

    # Good - Clear progression
    task "Load Data":
        step "Read File":
            grades = load_csv("grades.csv")

    task "Process Data":
        step "Calculate Average":
            total = sum(grades)
            average = total / len(grades)

    # Bad - Mixed responsibilities
    task "Do Everything":
        step "Process":
            grades = load_csv("grades.csv")
            total = sum(grades)
            average = total / len(grades)

Steps
^^^^^

Steps represent specific actions within a task. Each step should do one thing clearly.

**Naming Conventions:**

- Use descriptive action verbs
- Be specific about what the step does
- Use natural, readable phrases

.. code-block:: python

    # Good
    step "Initialize Variables":
        count = 0
        total = 0

    # Bad - too vague
    step "Setup":
        count = 0
        total = 0

**Size and Scope:**

- Each step should do one thing
- Keep steps focused and small
- Avoid deep nesting

.. code-block:: python

    # Good
    step "Calculate Total":
        total = score1 + score2 + score3

    step "Calculate Average":
        average = total / 3

    # Bad - too many responsibilities
    step "Do Calculations":
        total = score1 + score2 + score3
        average = total / 3
        decide:
            if average >= 90 then:
                grade = "A"
            else:
                grade = "B"

Subtasks
^^^^^^^^

Subtasks are reusable computations that return values. They act like functions within your tasks.

**When to Use Subtasks:**

- For reusable computations
- When code needs to return a value
- For complex operations that can be broken down

**Naming and Usage:**

.. code-block:: python

    # Good - Clear purpose and return value
    subtask "Calculate Average":
        total = sum(scores)
        return total / len(scores)

    step "Process Results":
        avg = Calculate_Average()
        print("Average:", avg)

    # Bad - Unclear purpose
    subtask "Process":
        return total / count

Code Layout
-----------

Indentation
^^^^^^^^^^^

- Use consistent indentation
- Each level should be clearly visible
- Align related code blocks

.. code-block:: python

    # Good
    task "Process Data":
        step "Initialize":
            count = 0
            total = 0

    # Bad - inconsistent indentation
    task "Process Data":
      step "Initialize":
            count = 0
          total = 0

Whitespace
^^^^^^^^^^

**Around Operators:**

.. code-block:: python

    # Good
    average = total / count
    name = first + " " + last

    # Bad
    average=total/count
    name=first+" "+last

**Block Structure:**

.. code-block:: python

    # Good - Clear separation between blocks
    task "First Task":
        step "Do Something":
            x = 1


    task "Second Task":
        step "Do Another":
            y = 2

Control Flow
------------

Decide Statements
^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Good
    decide:
        if score >= 90 then:
            grade = "A"
        elif score >= 80 then:
            grade = "B"
        else:
            grade = "C"

Loops
^^^^^

.. code-block:: python

    # Good
    for item in items:
        total = total + item
    end

    # For enumeration
    for index, value in enumerate(items):
        print(index, value)
    end

    # Range-based loop
    for i in range(5):
        print(i)
    end

Program Organization
--------------------

Run Statements
^^^^^^^^^^^^^^

Run statements should be organized logically and grouped by related functionality:

.. code-block:: python

    # Good - Clear execution flow
    run "Load Data"
    run "Validate Input"
    run "Calculate Results"
    run "Generate Report"

Best Practices
--------------

1. **Code Reuse**
    - Extract common logic into subtasks
    - Avoid duplicating code
    - Keep functions focused

2. **Maintainability**
    - Write self-documenting code through clear naming
    - Use consistent naming conventions
    - Follow logical organization

3. **Readability**
    - Prioritize clarity over cleverness
    - Maintain consistent style
    - Use meaningful names

Remember
-------

The primary goal of these guidelines is to make Think code more readable, maintainable, and understandable. When in doubt, choose clarity over convenience.