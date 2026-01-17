# zoo-template-common

Common execution handler and utilities for ZOO-Project CWL workflow templates.

## Overview

This package provides a simple, extensible base class (`CommonExecutionHandler`) for handling CWL workflow execution in ZOO-Project templates. It includes basic functionality for STAC catalog processing, pod configuration, and output management.

## Features

- **CommonExecutionHandler**: Base class for CWL workflow execution handlers
  - Pre/post execution hooks
  - STAC catalog output processing
  - Pod environment variable and node selector management
  - Secrets handling
  - Tool log management

- **CustomStacIO**: STAC I/O class for S3 operations using boto3
  - Read/write STAC catalogs from/to S3
  - Support for both S3 and local file systems

## Installation

```bash
pip install zoo-template-common
```

Or from Git:
```bash
pip install git+https://github.com/ZOO-Project/zoo-template-common.git@main
```

## Usage

### Basic Usage

```python
from zoo_template_common import CommonExecutionHandler
from zoo_calrissian_runner import ZooCalrissianRunner

def my_workflow(conf, inputs, outputs):
    execution_handler = CommonExecutionHandler(conf=conf, outputs=outputs)

    runner = ZooCalrissianRunner(
        cwl=cwl,
        conf=conf,
        inputs=inputs,
        outputs=outputs,
        execution_handler=execution_handler,
    )

    exit_status = runner.execute()
    return exit_status
```

### Extending CommonExecutionHandler

For specific use cases (e.g., EOEPCA with Workspace API integration), extend the base class:

```python
from zoo_template_common import CommonExecutionHandler
import jwt
import requests

class EoepcaCalrissianRunnerExecutionHandler(CommonExecutionHandler):
    def __init__(self, conf, outputs):
        super().__init__(conf, outputs)
        # Add EOEPCA-specific initialization
        self.ades_rx_token = conf.get("auth_env", {}).get("jwt", "")
        self.workspace_url = conf.get("eoepca", {}).get("workspace_url", "")

    def pre_execution_hook(self):
        # Add JWT decoding, Workspace API lookup, etc.
        super().pre_execution_hook()
        # Your custom logic here

    def post_execution_hook(self, log, output, usage_report, tool_logs):
        # Add STAC catalog registration, etc.
        super().post_execution_hook(log, output, usage_report, tool_logs)
        # Your custom logic here
```

## API Reference

### CommonExecutionHandler

#### Methods

- `__init__(conf, outputs=None)`: Initialize the handler
- `pre_execution_hook()`: Hook called before execution (override for custom behavior)
- `post_execution_hook(log, output, usage_report, tool_logs)`: Hook called after execution
- `setOutput(outputName, values)`: Process and set STAC catalog outputs
- `get_pod_env_vars()`: Get environment variables for the calrissian pod
- `get_pod_node_selector()`: Get node selector for the calrissian pod
- `get_additional_parameters()`: Get additional parameters for the execution
- `get_secrets()`: Get secrets for the calrissian pod
- `handle_outputs(log, output, usage_report, tool_logs)`: Register tool logs in service_logs

### CustomStacIO

Custom STAC IO class for S3 operations.

#### Methods

- `read_text(source, *args, **kwargs)`: Read text from S3 or local file
- `write_text(dest, txt, *args, **kwargs)`: Write text to S3 or local file

## Configuration

The handler expects configuration in the `conf` dictionary:

```python
conf = {
    "lenv": {
        "usid": "unique-execution-id",
        "Identifier": "workflow-name"
    },
    "main": {
        "tmpPath": "/tmp/zoo",
        "tmpUrl": "http://example.com/temp/"
    },
    "auth_env": {
        "user": "username"
    },
    "additional_parameters": {
        "region_name": "us-east-1",
        "endpoint_url": "https://s3.amazonaws.com",
        "aws_access_key_id": "ACCESS_KEY",
        "aws_secret_access_key": "SECRET_KEY"
    }
}
```

## Templates Using This Package

- **eoepca-proc-service-template**: Extends CommonExecutionHandler with EOEPCA Workspace API integration
- **zoo-service-template** (EOAP): Can use CommonExecutionHandler as-is or extend it

## Development

```bash
# Clone the repository
git clone https://github.com/ZOO-Project/zoo-template-common.git
cd zoo-template-common

# Install in development mode
pip install -e .
```

## Requirements

- Python >= 3.8
- loguru >= 0.7.0
- pystac >= 1.8.0
- pyyaml >= 6.0
- boto3 >= 1.28.0
- botocore >= 1.31.0

## License

Apache License 2.0

## Contributing

Contributions are welcome! Please submit a Pull Request.
