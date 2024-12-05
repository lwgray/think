=======================
Think Language Syntax
=======================

Think is designed to make problem decomposition explicit and clear. This guide covers the core syntax elements of the language.

Program Structure
-----------------

Every Think program has three main components:

1. An objective statement
2. One or more tasks
3. Run statements

Basic Example:

.. code-block:: python

   objective "Your goal here"
   
   task "Task Name":
       # Task contents
   
   run "Task Name"

Core Components
---------------

Objective
^^^^^^^^^
The objective statement declares your program's purpose:

.. code-block:: python

   objective "Calculate student grades"

Tasks
^^^^^
Tasks organize your solution into major components:

.. code-block:: python

   task "Process Data":
       step "Initialize":
           data = [1, 2, 3]

Steps
^^^^^
Steps perform specific actions:

.. code-block:: python

   step "Get user input":
       name = "Alice"
       age = 25

Subtasks
^^^^^^^^
Subtasks are reusable pieces that must return values:

.. code-block:: python

   subtask "Calculate Average":
       total = sum(scores)
       count = len(scores)
       return total / count

Control Flow
------------

Decision Making
^^^^^^^^^^^^^^^

Use decide blocks for conditional execution:

.. code-block:: python

   decide:
       if score >= 90 then:
           grade = "A"
       elif score >= 80 then:
           grade = "B"
       else:
           grade = "C"

Loops
^^^^^

Three types of loops are available:

1. Basic for loop:

.. code-block:: python

   for item in items:
       print(item)
   end

2. Range loop:

.. code-block:: python

   for i in range(5):
       print(i)
   end

3. Enumerate loop:

.. code-block:: python

   for index, value in enumerate(items):
       print(index, value)
   end

Data Types
----------

Numbers
^^^^^^^
.. code-block:: python

   integer = 42
   float_number = 3.14
   scientific = 1.5e-10

Strings
^^^^^^^
.. code-block:: python

   name = "Alice"
   message = 'Hello, ' + name

Lists
^^^^^
.. code-block:: python

   numbers = [1, 2, 3, 4, 5]
   mixed = [1, "two", 3.0]

Dictionaries
^^^^^^^^^^^^
.. code-block:: python

   person = {
       "name": "Alice",
       "age": 25,
       "scores": [85, 92, 88]
   }

Built-in Functions
------------------

Think provides several built-in functions:

* print(): Display output
* sum(): Calculate total of a list
* len(): Get length of a collection
* range(): Generate sequence of numbers

Operations
----------

Arithmetic
^^^^^^^^^^
.. code-block:: python

   sum = a + b
   difference = a - b
   product = a * b
   quotient = a / b

Comparisons
^^^^^^^^^^^
.. code-block:: python

   equals = a == b
   not_equals = a != b
   greater = a > b
   less = a < b
   greater_equals = a >= b
   less_equals = a <= b

Complete Example
----------------

Here's a complete example showing multiple features:

.. code-block:: python

   objective "Analyze student grades"

   task "Process Grades":
       step "Initialize data":
           grades = [85, 92, 78, 90, 88]
       
       subtask "Calculate Average":
           total = sum(grades)
           avg = total / len(grades)
           return avg
       
       subtask "Determine Performance":
           avg = calculate_average()
           decide:
               if avg >= 90 then:
                   return "Excellent"
               elif avg >= 80 then:
                   return "Good"
               else:
                   return "Needs Improvement"
           
       step "Show Results":
           performance = determine_performance()
           print("Class performance:", performance)

   run "Process Grades"

Another Example: Temperature Analysis
-------------------------------------

.. code-block:: python

   objective "Analyze temperature data"

   task "Process Temperatures":
       step "Get Data":
           temps = [72, 75, 68, 70, 73]
       
       subtask "Find Average":
           return sum(temps) / len(temps)
       
       subtask "Find Range":
           lowest = temps[0]
           highest = temps[0]
           
           for temp in temps:
               decide:
                   if temp < lowest then:
                       lowest = temp
                   if temp > highest then:
                       highest = temp
           end
           
           return highest - lowest
       
       step "Show Analysis":
           avg = find_average()
           range = find_range()
           print("Average temperature:", avg)
           print("Temperature range:", range)
   
   run "Process Temperatures"

Best Practices
--------------

1. Use clear, descriptive names for tasks and steps
2. Keep tasks focused on a single responsibility
3. Use subtasks for reusable calculations
4. Keep steps small and focused
5. Use meaningful step names
6. Add comments for complex logic
7. Follow consistent indentation

Quick Reference
---------------

Program Structure
^^^^^^^^^^^^^^^^^
* objective "..."
* task "..."
* step "..."
* subtask "..."
* run "..."

Control Flow
^^^^^^^^^^^^
* decide: if ... then: ... elif ... then: ... else: ...
* for ... in ...: ... end
* return ...

Operators
^^^^^^^^^
* Arithmetic: +, -, \*, /
* Comparison: ==, !=, >, <, >=, <=
* Assignment: =

Built-in Functions
^^^^^^^^^^^^^^^^^^
* print()
* sum()
* len()
* range()
* enumerate()