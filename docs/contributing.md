# Contributing to zoo-template-common

Thank you for your interest in contributing to `zoo-template-common`! This document provides guidelines for contributing to the project.

## Overview

`zoo-template-common` provides shared utilities and base service templates for ZOO-Project CWL runners, including `CommonExecutionHandler` and `CustomStacIO`. The project uses [Hatch](https://hatch.pypa.io/) as its build and development tool.

---

> **Important:** Always open your Pull Request against the `develop` branch, **not** `main`.
> Pull Requests targeting `main` directly will not be accepted.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- [Hatch](https://hatch.pypa.io/latest/install/) (`pip install hatch`)

### Development Setup

1. **Fork and Clone**

   ```bash
   git clone https://github.com/ZOO-Project/zoo-template-common.git
   cd zoo-template-common
   ```

2. **Install Hatch**

   ```bash
   pip install hatch
   ```

3. **Enter the Default Development Environment**

   Hatch automatically creates and manages a virtual environment for you:

   ```bash
   hatch shell
   ```

   This installs all dependencies defined under `[tool.hatch.envs.default]` in `pyproject.toml`.

4. **Verify Installation**

   ```bash
   python -c "from zoo_template_common import CommonExecutionHandler; print('OK')"
   ```

---

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use these prefixes:

- `feature/` — New features
- `fix/` — Bug fixes
- `docs/` — Documentation updates
- `refactor/` — Code refactoring
- `test/` — Test additions or fixes

### 2. Make Changes

Follow the coding standards described in the [Code Standards](#code-standards) section below.

### 3. Run Tests

The project uses `pytest` for testing via a dedicated Hatch environment:

```bash
# Run tests
hatch run test:test

# Run tests quietly
hatch run test:test-q
```

### 4. Update Documentation

- Update docstrings in the source code
- Update relevant `.md` files in `docs/`, if present

### 5. Commit Changes

Write clear, conventional commit messages:

```bash
git add .
git commit -m "feat: add support for custom STAC catalog handling"
```

Commit types:

- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation only
- `style` — Formatting, no logic change
- `refactor` — Code restructuring
- `test` — Adding or updating tests
- `chore` — Maintenance, dependency updates

### 6. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub with:

- **Base branch set to `develop`** — this is required
- A clear title and description
- Reference to any related issues (`Closes #123`)
- A summary of what changed and why
- Notes on any breaking changes

> **Reminder:** The base branch of your PR must be `develop`, not `main`.
> `main` is only updated by maintainers when cutting a release from `develop`.

---

## Hatch Environments

The project defines two Hatch environments in `pyproject.toml`:

| Environment | Purpose | Key Command |
|---|---|---|
| `default` | Day-to-day development | `hatch shell` |
| `test` | Running tests | `hatch run test:test` |

---

## Code Standards

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use **type hints** on all public methods
- Use **Google-style docstrings**
- Minimum Python version: **3.10**
- Code is formatted with [`black`](https://black.readthedocs.io/) (line length 100) and import-sorted with [`isort`](https://pycqa.github.io/isort/) (black profile) — run these before committing if your editor doesn't do it automatically
- `pylint` configuration enforces a max line length of 100

**Good example:**

```python
def get_stac_catalog(self, location: str) -> dict:
    """
    Load a STAC catalog from a local or S3 location.

    Args:
        location: Path or S3 URI to the STAC catalog.

    Returns:
        A dictionary representing the parsed STAC catalog.

    Raises:
        ValueError: If location is empty or invalid.
    """
    if not location:
        raise ValueError("location must not be empty")
    ...
```

### Error Handling

````python
try:
    import zoo
except ImportError:
    from zoo_runner_common import ZooStub
    zoo = ZooStub()

def load_config(self, path: str) -> dict:
    """Load configuration from a YAML file."""
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        zoo.update_status(conf, 0)  
        return {}
    except yaml.YAMLError as e:
        raise
````

### Versioning

The package version is managed in `zoo_template_common/__about__.py`. Do **not** manually edit the version; it is updated as part of the release process.

---

## Testing Guidelines

### Unit Tests

Place unit tests under `tests/` and name files `test_*.py`. Test discovery is configured via `[tool.pytest.ini_options]` (`testpaths = ["tests"]`):

```python
# tests/test_handlers.py
import unittest
from zoo_template_common import CommonExecutionHandler

class TestCommonExecutionHandler(unittest.TestCase):

    def test_initialization(self):
        """Test that the handler initializes correctly."""
        conf = {"lenv": {"message": ""}}
        handler = CommonExecutionHandler(conf=conf)
        self.assertIsNotNone(handler)
```

---

## Release Process

Releases are managed by project maintainers:

1. Ensure all changes are merged into `develop` and tested
2. Update the version in `zoo_template_common/__about__.py`
3. Update `CHANGELOG.md`
4. Create a new release on GitHub with the tag targeting the `develop` branch
5. Once the release is published, merge `develop` into `main`

---

## Getting Help

- **Bug reports / feature requests**: [Open an issue](https://github.com/ZOO-Project/zoo-template-common/issues)

---

## License

By contributing, you agree that your contributions will be licensed under the **Apache License 2.0**, the same license as this project.

---

Thank you for contributing! 🎉
