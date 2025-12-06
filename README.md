# Fields

A Python package for field management and processing.

## Installation

### From Source
```bash
pip install .
```

### For Development
```bash
pip install -e .[dev]
```

## Usage

```python
import fields

# Your code here
```

## Development

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]
```

### Testing
```bash
pytest
```

### Code Quality
```bash
# Format code
black .
isort .

# Lint code
flake8 fields tests
mypy fields
```

### Building Documentation
```bash
pip install -e .[docs]
sphinx-build docs docs/_build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Ensure all tests pass: `pytest`
6. Format code: `black . && isort .`
7. Submit a pull request

## License

MIT License - see LICENSE file for details.
