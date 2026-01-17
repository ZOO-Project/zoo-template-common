# Basic Usage

This guide covers the basic usage of `zoo-template-common` in your ZOO services.

## Simple Handler

The most basic usage extends `CommonExecutionHandler`:

```python
from zoo_template_common import CommonExecutionHandler

class MyExecutionHandler(CommonExecutionHandler):
    """Custom execution handler"""
    
    def __init__(self, conf, outputs=None):
        super().__init__(conf, outputs)
```

## Pre-Execution Hook

Override `pre_execution_hook()` to perform setup before workflow execution:

```python
class MyExecutionHandler(CommonExecutionHandler):
    def pre_execution_hook(self):
        """Setup before execution"""
        # Load configuration
        self.config = self.load_config()
        
        # Validate inputs
        if not self.validate_inputs():
            raise ValueError("Invalid inputs")
            
        # Setup environment
        os.environ["CUSTOM_VAR"] = "value"
```

## Post-Execution Hook

Override `post_execution_hook()` to process results after workflow execution:

```python
class MyExecutionHandler(CommonExecutionHandler):
    def post_execution_hook(self, log, output, usage_report, tool_logs):
        """Process results after execution"""
        # Call parent to setup S3 environment
        super().post_execution_hook(log, output, usage_report, tool_logs)
        
        # Custom processing
        self.process_outputs(output)
        self.send_notification()
```

## Output Processing

Use `setOutput()` to process STAC catalogs:

```python
class MyExecutionHandler(CommonExecutionHandler):
    def process_results(self, results_path):
        """Process workflow results"""
        # setOutput handles STAC catalog processing
        self.setOutput("result", {
            "stac": results_path,
            "type": "application/json"
        })
```

## Pod Configuration

Customize pod environment and node selection:

```python
class MyExecutionHandler(CommonExecutionHandler):
    def get_pod_env_vars(self):
        """Custom pod environment variables"""
        env_vars = super().get_pod_env_vars()
        env_vars.update({
            "CUSTOM_ENV": "value",
            "API_KEY": self.get_secret("api_key")
        })
        return env_vars
    
    def get_pod_node_selector(self):
        """Select specific nodes"""
        return {
            "workload": "processing",
            "gpu": "true"
        }
```

## Additional Parameters

Add custom parameters to workflow execution:

```python
class MyExecutionHandler(CommonExecutionHandler):
    def get_additional_parameters(self):
        """Custom workflow parameters"""
        params = super().get_additional_parameters()
        params["max_cores"] = 8
        params["max_ram"] = "16G"
        return params
```

## Secrets Management

Load secrets from YAML files:

```python
class MyExecutionHandler(CommonExecutionHandler):
    def setup_credentials(self):
        """Load and use secrets"""
        secrets = self.get_secrets()
        
        api_key = secrets.get("api_key")
        db_password = secrets.get("db_password")
        
        # Use secrets
        self.configure_api(api_key)
        self.connect_database(db_password)
```

Secrets are loaded from:
- `/var/etc/secrets/processing_secrets.yaml`
- `/var/etc/zoo-services-user/processing_secrets.yaml`

## Complete Example

```python
from zoo_template_common import CommonExecutionHandler
import os

class ProcessingHandler(CommonExecutionHandler):
    """Handler for data processing workflows"""
    
    def pre_execution_hook(self):
        """Setup processing environment"""
        # Load secrets
        secrets = self.get_secrets()
        os.environ["S3_KEY"] = secrets.get("s3_access_key", "")
        os.environ["S3_SECRET"] = secrets.get("s3_secret_key", "")
        
        # Validate configuration
        required = ["input_data", "output_bucket"]
        for key in required:
            if key not in self.conf["lenv"]:
                raise ValueError(f"Missing required parameter: {key}")
    
    def post_execution_hook(self, log, output, usage_report, tool_logs):
        """Process results"""
        # Setup S3 environment
        super().post_execution_hook(log, output, usage_report, tool_logs)
        
        # Log execution stats
        self.log_stats(usage_report)
        
        # Register tool logs
        self.handle_outputs(log, output, usage_report, tool_logs)
    
    def get_pod_env_vars(self):
        """Configure pod environment"""
        env_vars = super().get_pod_env_vars()
        env_vars["PROCESSING_MODE"] = "batch"
        env_vars["LOG_LEVEL"] = "INFO"
        return env_vars
    
    def get_pod_node_selector(self):
        """Select compute nodes"""
        return {"node-type": "compute-optimized"}
    
    def get_additional_parameters(self):
        """Workflow parameters"""
        return {
            "max_cores": 16,
            "max_ram": "32G",
            "timeout": 3600
        }
    
    def log_stats(self, usage_report):
        """Log execution statistics"""
        if usage_report:
            print(f"Execution time: {usage_report.get('duration', 'N/A')}")
            print(f"Memory used: {usage_report.get('memory', 'N/A')}")
```

## Error Handling

Handle errors gracefully:

```python
class MyExecutionHandler(CommonExecutionHandler):
    def safe_execute(self):
        """Execute with error handling"""
        try:
            self.pre_execution_hook()
            result = self.run_workflow()
            self.post_execution_hook(None, result, None, None)
            return True
        except ValueError as e:
            self.conf["lenv"]["message"] = f"Validation error: {e}"
            return False
        except Exception as e:
            self.conf["lenv"]["message"] = f"Execution failed: {e}"
            return False
```

## Next Steps

- Learn about [extending the handler](extending.md)
- See [complete examples](examples.md)
- Read the [API reference](../api-reference/common-execution-handler.md)
