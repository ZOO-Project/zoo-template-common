# Quick Start

This guide will help you get started with zoo-template-common.

## Basic Usage

### 1. Import the Handler

```python
from zoo_template_common import CommonExecutionHandler
from zoo_calrissian_runner import ZooCalrissianRunner
import yaml
```

### 2. Create an Execution Handler

```python
def my_workflow(conf, inputs, outputs):
    # Create the execution handler
    execution_handler = CommonExecutionHandler(conf=conf, outputs=outputs)
    
    # Load CWL workflow
    with open("app-package.cwl", "r") as f:
        cwl = yaml.safe_load(f)
    
    # Create the runner
    runner = ZooCalrissianRunner(
        cwl=cwl,
        conf=conf,
        inputs=inputs,
        outputs=outputs,
        execution_handler=execution_handler,
    )
    
    # Execute
    exit_status = runner.execute()
    
    return exit_status
```

### 3. Process Outputs

The handler automatically processes STAC catalog outputs and sets up the environment for S3 operations.

## Extending the Handler

For custom behavior, extend `CommonExecutionHandler`:

```python
from zoo_template_common import CommonExecutionHandler

class MyCustomHandler(CommonExecutionHandler):
    def pre_execution_hook(self):
        """Custom logic before execution"""
        super().pre_execution_hook()
        # Your custom code here
        
    def post_execution_hook(self, log, output, usage_report, tool_logs):
        """Custom logic after execution"""
        # Your custom code here
        super().post_execution_hook(log, output, usage_report, tool_logs)
```

## Configuration

The handler expects a configuration dictionary:

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

## Next Steps

- Learn more about [Basic Usage](../user-guide/basic-usage.md)
- Learn about [Extending the Handler](../user-guide/extending.md)
- Explore [Complete Examples](../user-guide/examples.md)
- Read the [API Reference](../api-reference/common-execution-handler.md)
