# Installation

## Requirements

- Python >= 3.8
- pip or poetry

## Install from PyPI

```bash
pip install zoo-template-common
```

## Install from Git

### Latest release
```bash
pip install git+https://github.com/ZOO-Project/zoo-template-common.git@main
```

### Specific branch
```bash
pip install git+https://github.com/ZOO-Project/zoo-template-common.git@feature/pythoupdates
```

## Development Installation

For development, clone the repository and install in editable mode:

```bash
git clone https://github.com/ZOO-Project/zoo-template-common.git
cd zoo-template-common
pip install -e .
```

## Dependencies

The package automatically installs the following dependencies:

- loguru >= 0.7.0
- pystac >= 1.8.0
- pyyaml >= 6.0
- boto3 >= 1.28.0
- botocore >= 1.31.0

## Verify Installation

```python
python -c "from zoo_template_common import CommonExecutionHandler; print('Installation successful')"
```
