# API Reference

Complete documentation of Think's API, including core classes, functions, and modules.

## Core Modules

### Parser (`think.parser`)

```{eval-rst}
.. automodule:: think.parser
   :members:
   :undoc-members:
   :show-inheritance:
```

#### Key Classes
- `ThinkParser`: Main parser class
- `ThinkLexer`: Lexical analyzer

### Interpreter (`think.interpreter`)

```{eval-rst}
.. automodule:: think.interpreter
   :members:
   :undoc-members:
   :show-inheritance:
```

#### Key Classes
- `ThinkInterpreter`: Program execution engine
- `ExecutionContext`: Runtime context manager

### Validator (`think.validator`)

```{eval-rst}
.. automodule:: think.validator
   :members:
   :undoc-members:
   :show-inheritance:
```

#### Key Classes
- `ThinkValidator`: Program structure validator
- `ValidationContext`: Validation state manager

### Jupyter Integration (`think.jupyter_magic`)

```{eval-rst}
.. automodule:: think.jupyter_magic
   :members:
   :undoc-members:
   :show-inheritance:
```

#### Key Classes
- `ThinkMagics`: Jupyter extension handler

## Error Handling (`think.errors`)

```{eval-rst}
.. automodule:: think.errors
   :members:
   :undoc-members:
   :show-inheritance:
```

### Error Classes
- `ThinkError`: Base error class
- `ThinkParserError`: Parsing errors
- `ThinkRuntimeError`: Execution errors

## Built-in Functions

### Mathematical Operations
- `sum(iterable)`: Calculate sum of values
- `min(iterable)`: Find minimum value
- `max(iterable)`: Find maximum value
