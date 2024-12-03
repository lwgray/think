# Installation

Think can be installed in several ways, depending on your needs.

## Quick Install

The simplest way to install Think is via pip:

```bash
pip install think-lang
```

## Development Installation

For development or the latest features, install from source:

```bash
git clone https://github.com/lwgray/think.git
cd think
pip install -e ".[dev]"
```

## Requirements

Think requires:

- Python 3.7 or higher
- PLY (Python Lex-Yacc)
- IPython/Jupyter (for notebook support)

All dependencies will be automatically installed when you install Think.

## Platform Support

Think is supported on:
- Linux (all major distributions)
- macOS (10.14+)
- Windows 10/11

## Verifying Installation

To verify your installation:

```python
import think
print(think.__version__)
```

## Jupyter Integration

To use Think in Jupyter notebooks:

1. Install Jupyter if not already installed:
```bash
pip install jupyter
```

2. Load the Think extension in your notebook:
```python
%load_ext think.jupyter_magic
```

## Development Requirements

If you plan to contribute to Think, install additional development dependencies:

```bash
pip install -r requirements-dev.txt
```

This includes:
- pytest for testing
- black for code formatting
- mypy for type checking
- sphinx for documentation

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```
   ImportError: No module named 'think'
   ```
   Solution: Verify installation with `pip list | grep think`

2. **Jupyter Extension Not Found**
   ```
   ModuleNotFoundError: No module named 'think.jupyter_magic'
   ```
   Solution: Reinstall with `pip install -e ".[jupyter]"`

3. **Version Conflicts**
   ```
   pkg_resources.VersionConflict
   ```
   Solution: Create a new virtual environment:
   ```bash
   python -m venv thinkenv
   source thinkenv/bin/activate  # On Windows: thinkenv\Scripts\activate
   pip install think-lang
   ```

### Getting Help

If you encounter issues:

1. Check our [GitHub Issues](https://github.com/lwgray/think/issues)
2. Join our [Discord community](https://discord.gg/think)
3. Email support at support@think-lang.org

## Next Steps

After installation:
1. Try the [Quickstart Guide](quickstart.html)
2. Explore [Tutorials](tutorials/index.html)
3. Read the [User Guide](user_guide/index.html)
