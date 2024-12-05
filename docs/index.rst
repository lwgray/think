Welcome to Think Documentation
==============================

Think is an educational programming language designed to teach computational thinking through explicit problem decomposition. It helps users break down complex problems into manageable parts while providing interactive feedback.


Getting Started
---------------

Installation
^^^^^^^^^^^^

.. code-block:: bash

   pip install think-lang

Quick Example
^^^^^^^^^^^^^

.. code-block:: python

   objective "Calculate student grades"

   task "Process Grades":
       step "Get scores":
           scores = [85, 92, 78]

       subtask "Calculate Average":
           total = sum(scores)
           return total / len(scores)

   run "Process Grades"

Key Features
------------

* Structured problem solving with objectives, tasks, subtasks, and steps
* Interactive execution with real-time feedback
* Built-in explanation mode for learning
* Jupyter notebook integration
* Python-inspired syntax with educational focus
