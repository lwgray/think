=====================================================
Think: A Language for Learning Computational Thinking
=====================================================

Think is an educational programming language designed to teach computational thinking through explicit problem decomposition. It helps users break down complex problems into manageable parts while providing interactive feedback.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   syntax_guide

Installation
------------

.. code-block:: bash

   pip install think-lang

Quick Example
-------------

.. code-block:: python

   objective "Calculate student grades"

   task "Process Grades":
       step "Get scores":
           scores = [85, 92, 78]

       subtask "Calculate Average":
           total = sum(scores)
           return total / len(scores)

   run "Process Grades"

Features
--------

* Structured problem solving with objectives, tasks, subtasks, and steps
* Interactive execution with real-time feedback
* Built-in explanation mode for learning
* Jupyter notebook integration
* Python-inspired syntax with educational focus

Using Think in Jupyter Notebooks
--------------------------------

Think provides seamless integration with Jupyter notebooks through magic commands.

Loading the Extension
^^^^^^^^^^^^^^^^^^^^^

First, load the Think extension:

.. code-block:: python

   %load_ext think.jupyter_magic

Basic Usage
^^^^^^^^^^^

Use the ``%%think`` cell magic to execute Think code:

.. code-block:: python

   %%think
   objective "Hello World"
   
   task "Greet":
       step "Print message":
           print("Hello from Think!")
   
   run "Greet"

Explain Mode
^^^^^^^^^^^^

Enable explanation mode using the --explain flag:

.. code-block:: python

   %%think --explain
   objective "Calculate average"
   
   task "Process Numbers":
       step "Initialize data":
           numbers = [1, 2, 3, 4, 5]
       
       subtask "Calculate Mean":
           total = sum(numbers)
           return total / len(numbers)

        step "Print result":
            print("Mean:", calculate_mean(numbers))
   
   run "Process Numbers"

.. code-block:: python

    [PROGRAM] Calculate average
[TASK] Executing Process Numbers
  [STEP] Executing Initialize data
    [VARIABLE] Assigned [1, 2, 3, 4, 5] to numbers
  [SUBTASK] Executing Calculate Mean
    [VARIABLE] Assigned 15 to total
  [STEP] Executing Print result
    [SUBTASK] Executing Calculate Mean
      [VARIABLE] Assigned 15 to total
    [OUTPUT] Mean: 3


Available Styles
^^^^^^^^^^^^^^^^

Choose from different output styles:

* default: Standard bracketed format
* minimal: Clean, simple format
* detailed: With separators
* color: With ANSI colors
* markdown: Using Markdown-style headers
* educational: With emoji icons

Example with style:

.. code-block:: python

   %%think --explain --style educational
    objective "Calculate average"
   
   task "Process Numbers":
       step "Initialize data":
           numbers = [1, 2, 3, 4, 5]
       
       subtask "Calculate Mean":
           total = sum(numbers)
           return total / len(numbers)

        step "Print result":
            print("Mean:", calculate_mean(numbers))
   
   run "Process Numbers"

   • Calculate average
• Executing Process Numbers
  • Executing Initialize data
    📝 Assigned [1, 2, 3, 4, 5] to numbers
  • Executing Calculate Mean
    📝 Assigned 15 to total
  • Executing Print result
    • Executing Calculate Mean
      📝 Assigned 15 to total
    📤 Output: Mean: 3


Magic Command Options
^^^^^^^^^^^^^^^^^^^^^

* --explain: Enable explanation mode
* --style STYLE: Set output style

For more details about the language syntax, see :doc:`syntax_guide`.