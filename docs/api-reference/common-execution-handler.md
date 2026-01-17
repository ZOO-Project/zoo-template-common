# CommonExecutionHandler API Reference

::: zoo_template_common.common_execution_handler.CommonExecutionHandler
    options:
      show_source: true
      show_root_heading: true
      heading_level: 2

## Class Overview

`CommonExecutionHandler` is the base class for all CWL workflow execution handlers in ZOO-Project services.

## Constructor

```python
def __init__(self, conf, outputs=None)
```

**Parameters:**

- `conf` (dict): ZOO configuration dictionary containing service configuration and environment
- `outputs` (dict, optional): ZOO outputs dictionary for storing results

**Example:**

```python
handler = CommonExecutionHandler(conf, outputs)
```

## Methods

### pre_execution_hook()

Called before workflow execution. Override to perform setup tasks.

```python
def pre_execution_hook(self):
    """Hook called before execution"""
    pass
```

**Use cases:**
- Load configuration
- Validate inputs
- Setup environment variables
- Initialize connections

**Example:**

```python
def pre_execution_hook(self):
    secrets = self.get_secrets()
    os.environ["API_KEY"] = secrets.get("api_key")
```

### post_execution_hook()

Called after workflow execution. Override to process results.

```python
def post_execution_hook(self, log, output, usage_report, tool_logs):
    """Hook called after execution"""
    # Setup S3 environment
    os.environ["S3_ENDPOINT"] = self.conf.get("eoepca", {}).get("S3", {}).get("url", "")
```

**Parameters:**

- `log`: Execution log
- `output`: Workflow output data
- `usage_report`: Resource usage statistics
- `tool_logs`: Tool-specific logs

**Use cases:**
- Process workflow outputs
- Save results
- Send notifications
- Cleanup resources

**Example:**

```python
def post_execution_hook(self, log, output, usage_report, tool_logs):
    super().post_execution_hook(log, output, usage_report, tool_logs)
    self.save_results(output)
    self.send_notification("completed")
```

### setOutput()

Process and set output values, handles STAC catalog processing.

```python
def setOutput(self, outputName, values)
```

**Parameters:**

- `outputName` (str): Name of the output
- `values` (dict): Output values containing STAC catalog or data

**Behavior:**

- If `values` contains `"stac"` key, processes as STAC catalog
- Reads STAC catalog file
- Converts ItemCollections to Catalogs
- Updates output dictionary

**Example:**

```python
handler.setOutput("result", {
    "stac": "/tmp/catalog.json",
    "type": "application/json"
})
```

### get_pod_env_vars()

Get environment variables for pod/container execution.

```python
def get_pod_env_vars(self) -> dict
```

**Returns:**
- dict: Environment variables to set in execution pod

**Default:**
- Empty dictionary

**Example:**

```python
def get_pod_env_vars(self):
    env_vars = super().get_pod_env_vars()
    env_vars["CUSTOM_VAR"] = "value"
    env_vars["LOG_LEVEL"] = "DEBUG"
    return env_vars
```

### get_pod_node_selector()

Get node selector for pod scheduling.

```python
def get_pod_node_selector(self) -> dict
```

**Returns:**
- dict: Node selector labels for Kubernetes scheduling

**Default:**
- Empty dictionary

**Example:**

```python
def get_pod_node_selector(self):
    return {
        "workload": "processing",
        "gpu": "true"
    }
```

### get_additional_parameters()

Get additional parameters for workflow execution.

```python
def get_additional_parameters(self) -> dict
```

**Returns:**
- dict: Additional parameters for the workflow

**Default:**
- Empty dictionary

**Example:**

```python
def get_additional_parameters(self):
    return {
        "max_cores": 8,
        "max_ram": "16G",
        "timeout": 3600
    }
```

### get_secrets()

Load secrets from YAML configuration files.

```python
def get_secrets(self) -> dict
```

**Returns:**
- dict: Secrets loaded from configuration files

**Searched paths:**
1. `/var/etc/secrets/processing_secrets.yaml`
2. `/var/etc/zoo-services-user/processing_secrets.yaml`

**Example:**

```python
secrets = handler.get_secrets()
api_key = secrets.get("api_key")
db_password = secrets.get("db_password")
```

### handle_outputs()

Register tool logs as workflow outputs.

```python
def handle_outputs(self, log, output, usage_report, tool_logs)
```

**Parameters:**

- `log`: Execution log
- `output`: Workflow outputs
- `usage_report`: Resource usage
- `tool_logs`: Tool execution logs

**Example:**

```python
handler.handle_outputs(log, output, usage_report, tool_logs)
```

### local_get_file()

Static method to load YAML file.

```python
@staticmethod
def local_get_file(fileName: str) -> dict
```

**Parameters:**

- `fileName` (str): Path to YAML file

**Returns:**
- dict: Parsed YAML content

**Example:**

```python
config = CommonExecutionHandler.local_get_file("/path/to/config.yaml")
```

## Attributes

### conf

ZOO configuration dictionary.

```python
handler.conf  # dict
```

**Structure:**
```python
{
    "lenv": {
        "message": "",  # Error/status messages
        "Identifier": "service-id"
    },
    "main": {
        "tmpPath": "/tmp"
    },
    "inputs": {...},  # Service inputs
    "eoepca": {  # EOEPCA configuration
        "S3": {
            "url": "https://s3.example.com"
        }
    }
}
```

### outputs

ZOO outputs dictionary.

```python
handler.outputs  # dict or None
```

**Structure:**
```python
{
    "result": {
        "value": "...",
        "mimeType": "application/json"
    }
}
```

## Usage Pattern

Typical usage pattern:

```python
class MyHandler(CommonExecutionHandler):
    def pre_execution_hook(self):
        # Setup
        super().pre_execution_hook()
        self.setup_environment()
    
    def post_execution_hook(self, log, output, usage_report, tool_logs):
        # Process results
        super().post_execution_hook(log, output, usage_report, tool_logs)
        self.process_results(output)
    
    def get_pod_env_vars(self):
        env = super().get_pod_env_vars()
        env["CUSTOM"] = "value"
        return env

# Use in ZOO service
def my_service(conf, inputs, outputs):
    handler = MyHandler(conf, outputs)
    handler.pre_execution_hook()
    # Execute workflow...
    handler.post_execution_hook(None, outputs, None, None)
    return 3  # SUCCESS
```

## See Also

- [CustomStacIO](custom-stac-io.md) - STAC I/O customization
- [Basic Usage](../user-guide/basic-usage.md) - Usage examples
- [Extending](../user-guide/extending.md) - Extension patterns
