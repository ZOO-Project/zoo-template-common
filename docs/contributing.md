# Contributing to zoo-template-common

Thank you for your interest in contributing to zoo-template-common! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Poetry (recommended) or pip

### Development Setup

1. **Fork and Clone**

```bash
git clone https://github.com/YOUR-USERNAME/zoo-template-common.git
cd zoo-template-common
```

2. **Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**

With Poetry:
```bash
poetry install
```

Or with pip:
```bash
pip install -e ".[dev]"
```

4. **Verify Installation**

```bash
python -c "from zoo_template_common import CommonExecutionHandler; print('OK')"
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use prefixes:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring

### 2. Make Changes

Follow the coding standards:

- **PEP 8**: Follow Python style guide
- **Type Hints**: Use type annotations
- **Docstrings**: Google-style docstrings
- **Comments**: Explain complex logic

**Example:**

```python
def get_pod_env_vars(self) -> dict:
    """
    Get environment variables for pod execution.
    
    Returns:
        dict: Environment variables to set in the execution pod.
            Keys are variable names, values are variable values.
    
    Example:
        >>> handler = CommonExecutionHandler(conf)
        >>> env = handler.get_pod_env_vars()
        >>> print(env["MY_VAR"])
        'value'
    """
    return {}
```

### 3. Write Tests

Add tests for new features:

```python
# tests/test_my_feature.py
import pytest
from zoo_template_common import CommonExecutionHandler

def test_my_feature():
    """Test my new feature"""
    conf = {"lenv": {"message": ""}}
    handler = CommonExecutionHandler(conf)
    
    # Test your feature
    result = handler.my_feature()
    assert result == expected_value
```

Run tests:

```bash
pytest tests/
```

### 4. Update Documentation

- Update docstrings
- Update relevant `.md` files in `docs/`
- Add examples if applicable

### 5. Commit Changes

Write clear commit messages:

```bash
git add .
git commit -m "Add feature: description of feature"
```

Good commit message format:
```
<type>: <short summary>

<detailed description if needed>

<issue reference if applicable>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Create a Pull Request on GitHub with:
- Clear title and description
- Reference related issues
- List changes made
- Add screenshots if UI-related

## Code Standards

### Python Style

```python
# Good
def get_secrets(self) -> dict:
    """Load secrets from configuration files."""
    secrets = {}
    for path in self.SECRET_PATHS:
        if os.path.exists(path):
            secrets.update(self.local_get_file(path))
    return secrets

# Bad
def get_secrets(self):
    s = {}
    for p in ["/var/etc/secrets/processing_secrets.yaml"]:
        if os.path.exists(p):
            s.update(self.local_get_file(p))
    return s
```

### Type Hints

```python
from typing import Dict, List, Optional

def process_items(self, items: List[str]) -> Dict[str, int]:
    """Process list of items."""
    pass

def get_config(self) -> Optional[Dict[str, any]]:
    """Get configuration if available."""
    pass
```

### Error Handling

```python
# Good
def load_file(self, path: str) -> dict:
    """Load YAML file."""
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        self.logger.warning(f"File not found: {path}")
        return {}
    except yaml.YAMLError as e:
        self.logger.error(f"Invalid YAML: {e}")
        raise

# Bad
def load_file(self, path):
    with open(path) as f:
        return yaml.safe_load(f)
```

## Testing Guidelines

### Unit Tests

Test individual methods:

```python
def test_get_pod_env_vars():
    """Test pod environment variables"""
    conf = {"lenv": {}}
    handler = CommonExecutionHandler(conf)
    
    env = handler.get_pod_env_vars()
    
    assert isinstance(env, dict)
    assert "CUSTOM_VAR" not in env  # Base handler returns empty
```

### Integration Tests

Test interactions:

```python
def test_handler_lifecycle():
    """Test complete handler lifecycle"""
    conf = {"lenv": {"message": ""}}
    outputs = {}
    
    handler = CommonExecutionHandler(conf, outputs)
    
    # Pre-execution
    handler.pre_execution_hook()
    
    # Execution simulation
    outputs["stac"] = "/tmp/catalog.json"
    
    # Post-execution
    handler.post_execution_hook(None, outputs, None, None)
    
    assert "message" in conf["lenv"]
```

### Test Coverage

Aim for >80% code coverage:

```bash
pytest --cov=zoo_template_common tests/
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def my_method(self, param1: str, param2: int = 0) -> bool:
    """
    Short description of method.
    
    Longer description with more details about what the method does,
    how it works, and any important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2. Defaults to 0.
    
    Returns:
        True if successful, False otherwise.
    
    Raises:
        ValueError: If param1 is empty
        IOError: If file cannot be read
    
    Example:
        >>> handler = MyHandler(conf)
        >>> result = handler.my_method("test", 5)
        >>> print(result)
        True
    """
    pass
```

### Update Documentation

When adding features:

1. Update API reference in `docs/api-reference/`
2. Add usage examples to `docs/user-guide/`
3. Update `README.md` if needed
4. Add to changelog

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release tag
4. Build and publish to PyPI

```bash
# Update version
poetry version patch  # or minor, major

# Build
poetry build

# Publish (maintainers only)
poetry publish
```

## Getting Help

- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Contact**: Email the maintainers

## Code of Conduct

Be respectful and professional:

- Be welcoming and inclusive
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Questions?

If you have questions about contributing, feel free to:

- Open an issue
- Start a discussion
- Contact the maintainers

Thank you for contributing! 🎉
