# zoo-template-common

Welcome to the documentation for **zoo-template-common**, a Python package providing common execution handlers and utilities for ZOO-Project CWL workflow templates.

## Overview

This package provides a simple, extensible base class (`CommonExecutionHandler`) for handling CWL workflow execution in ZOO-Project templates. It includes basic functionality for STAC catalog processing, pod configuration, and output management.

## Key Features

- **CommonExecutionHandler**: Base class for CWL workflow execution handlers
    - Pre/post execution hooks
    - STAC catalog output processing
    - Pod environment variable and node selector management
    - Secrets handling
    - Tool log management

- **CustomStacIO**: STAC I/O class for S3 operations using boto3
    - Read/write STAC catalogs from/to S3
    - Support for both S3 and local file systems

## Quick Example

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

## Templates Using This Package

- **eoepca-proc-service-template**: Extends CommonExecutionHandler with EOEPCA Workspace API integration
- **zoo-service-template** (EOAP): Uses CommonExecutionHandler as-is or extends it

## Installation

```bash
pip install zoo-template-common
```

Or from Git:
```bash
pip install git+https://github.com/EOEPCA/zoo-template-common.git@main
```

## Next Steps

- [Quick Start Guide](getting-started/quickstart.md)
- [Basic Usage](user-guide/basic-usage.md)
- [Extending the Handler](user-guide/extending.md)
- [Complete Examples](user-guide/examples.md)
- [API Reference](api-reference/common-execution-handler.md)
