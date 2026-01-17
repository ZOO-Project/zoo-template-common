# Extending CommonExecutionHandler

This guide shows how to extend `CommonExecutionHandler` for specialized use cases.

## Extension Patterns

### 1. Authentication Handler

Add authentication to your workflows:

```python
from zoo_template_common import CommonExecutionHandler
import jwt
import requests

class AuthenticatedHandler(CommonExecutionHandler):
    """Handler with JWT authentication"""
    
    def __init__(self, conf, outputs=None):
        super().__init__(conf, outputs)
        self.token = None
        self.username = None
    
    def pre_execution_hook(self):
        """Extract and validate JWT token"""
        # Get token from environment or conf
        token_str = os.environ.get("ACCESS_TOKEN") or \
                    self.conf["lenv"].get("access_token")
        
        if not token_str:
            raise ValueError("No access token provided")
        
        # Decode JWT
        try:
            self.token = jwt.decode(token_str, options={"verify_signature": False})
            self.username = self.token.get("preferred_username", "unknown")
        except Exception as e:
            raise ValueError(f"Invalid token: {e}")
        
        # Setup user-specific environment
        self.setup_user_environment()
    
    def setup_user_environment(self):
        """Configure environment for user"""
        os.environ["CURRENT_USER"] = self.username
        os.environ["USER_WORKSPACE"] = f"/workspaces/{self.username}"
```

### 2. Workspace Integration

Integrate with external workspace APIs:

```python
class WorkspaceHandler(AuthenticatedHandler):
    """Handler with workspace integration"""
    
    def __init__(self, conf, outputs=None):
        super().__init__(conf, outputs)
        self.workspace_api = None
    
    def pre_execution_hook(self):
        """Setup workspace connection"""
        super().pre_execution_hook()
        
        # Connect to workspace API
        workspace_url = os.environ.get("WORKSPACE_API_URL")
        self.workspace_api = WorkspaceClient(workspace_url, self.token)
        
        # Get storage credentials
        credentials = self.workspace_api.get_credentials(self.username)
        self.configure_storage(credentials)
    
    def post_execution_hook(self, log, output, usage_report, tool_logs):
        """Register results in workspace"""
        super().post_execution_hook(log, output, usage_report, tool_logs)
        
        # Register output catalog
        if "stac_catalog" in output:
            self.workspace_api.register_catalog(
                username=self.username,
                catalog_url=output["stac_catalog"]
            )
    
    def configure_storage(self, credentials):
        """Configure S3 storage"""
        os.environ["AWS_ACCESS_KEY_ID"] = credentials["access_key"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = credentials["secret_key"]
        os.environ["AWS_S3_ENDPOINT"] = credentials["endpoint"]
```

### 3. Custom STAC Processing

Override STAC processing behavior:

```python
class CustomStacHandler(CommonExecutionHandler):
    """Handler with custom STAC processing"""
    
    def setOutput(self, outputName, values):
        """Custom STAC processing"""
        # Pre-process values
        if "stac" in values:
            values = self.enhance_stac_catalog(values)
        
        # Call parent
        super().setOutput(outputName, values)
        
        # Post-process
        self.publish_catalog(outputName)
    
    def enhance_stac_catalog(self, values):
        """Add metadata to STAC items"""
        catalog_path = values.get("stac")
        
        # Load catalog
        from pystac import Catalog
        catalog = Catalog.from_file(catalog_path)
        
        # Add custom metadata
        for item in catalog.get_items():
            item.properties["processor"] = "custom-processor"
            item.properties["version"] = "1.0.0"
            item.properties["user"] = getattr(self, "username", "unknown")
        
        # Save enhanced catalog
        catalog.save()
        
        return values
    
    def publish_catalog(self, output_name):
        """Publish catalog to external service"""
        print(f"Publishing {output_name} to catalog service")
```

### 4. Monitoring and Metrics

Add monitoring capabilities:

```python
class MonitoredHandler(CommonExecutionHandler):
    """Handler with monitoring"""
    
    def __init__(self, conf, outputs=None):
        super().__init__(conf, outputs)
        self.metrics = {}
        self.start_time = None
    
    def pre_execution_hook(self):
        """Start monitoring"""
        import time
        self.start_time = time.time()
        self.metrics["status"] = "started"
        self.send_metric("workflow.started", 1)
        
        super().pre_execution_hook()
    
    def post_execution_hook(self, log, output, usage_report, tool_logs):
        """Record metrics"""
        import time
        duration = time.time() - self.start_time
        
        self.metrics["duration"] = duration
        self.metrics["status"] = "completed"
        
        super().post_execution_hook(log, output, usage_report, tool_logs)
        
        # Send metrics
        self.send_metric("workflow.duration", duration)
        self.send_metric("workflow.completed", 1)
        
        if usage_report:
            self.send_usage_metrics(usage_report)
    
    def send_metric(self, name, value):
        """Send metric to monitoring system"""
        # Implement your metrics backend
        print(f"METRIC {name}={value}")
    
    def send_usage_metrics(self, usage_report):
        """Send resource usage metrics"""
        for key, value in usage_report.items():
            self.send_metric(f"resource.{key}", value)
```

### 5. Multi-Backend Storage

Support multiple storage backends:

```python
class MultiStorageHandler(CommonExecutionHandler):
    """Handler supporting multiple storage backends"""
    
    def get_pod_env_vars(self):
        """Configure multiple storage backends"""
        env_vars = super().get_pod_env_vars()
        
        # Primary S3 storage
        env_vars["PRIMARY_S3_ENDPOINT"] = os.environ.get("S3_ENDPOINT")
        env_vars["PRIMARY_S3_BUCKET"] = os.environ.get("S3_BUCKET")
        
        # Secondary storage (e.g., Google Cloud)
        if os.environ.get("GCS_BUCKET"):
            env_vars["GCS_BUCKET"] = os.environ["GCS_BUCKET"]
            env_vars["GOOGLE_APPLICATION_CREDENTIALS"] = "/secrets/gcs-key.json"
        
        # Azure storage
        if os.environ.get("AZURE_STORAGE_ACCOUNT"):
            env_vars["AZURE_STORAGE_ACCOUNT"] = os.environ["AZURE_STORAGE_ACCOUNT"]
            env_vars["AZURE_STORAGE_KEY"] = self.get_secrets().get("azure_key")
        
        return env_vars
    
    def post_execution_hook(self, log, output, usage_report, tool_logs):
        """Replicate outputs to multiple backends"""
        super().post_execution_hook(log, output, usage_report, tool_logs)
        
        # Replicate to secondary storage
        if os.environ.get("GCS_BUCKET"):
            self.replicate_to_gcs(output)
        
        if os.environ.get("AZURE_STORAGE_ACCOUNT"):
            self.replicate_to_azure(output)
```

### 6. Validation and Quality Control

Add validation steps:

```python
class ValidatedHandler(CommonExecutionHandler):
    """Handler with validation"""
    
    def pre_execution_hook(self):
        """Validate inputs"""
        super().pre_execution_hook()
        
        # Validate required inputs
        self.validate_inputs()
        
        # Validate resources
        self.validate_resources()
    
    def post_execution_hook(self, log, output, usage_report, tool_logs):
        """Validate outputs"""
        super().post_execution_hook(log, output, usage_report, tool_logs)
        
        # Validate output quality
        if not self.validate_outputs(output):
            raise ValueError("Output validation failed")
        
        # Check STAC compliance
        self.validate_stac_catalog(output)
    
    def validate_inputs(self):
        """Validate input parameters"""
        required = ["input_data", "output_path"]
        for param in required:
            if param not in self.conf["lenv"]:
                raise ValueError(f"Missing required parameter: {param}")
    
    def validate_outputs(self, output):
        """Validate output data"""
        # Check output exists
        if not output or not output.get("stac"):
            return False
        
        # Validate file exists
        import os
        if not os.path.exists(output["stac"]):
            return False
        
        return True
    
    def validate_stac_catalog(self, output):
        """Validate STAC catalog structure"""
        from pystac import Catalog
        
        try:
            catalog = Catalog.from_file(output["stac"])
            catalog.validate()
        except Exception as e:
            raise ValueError(f"Invalid STAC catalog: {e}")
```

## Combining Extensions

Combine multiple extensions using multiple inheritance:

```python
class FullFeaturedHandler(
    MonitoredHandler,
    WorkspaceHandler,
    ValidatedHandler
):
    """Handler with all features"""
    
    def pre_execution_hook(self):
        """Combined pre-execution"""
        # Call all parent hooks
        MonitoredHandler.pre_execution_hook(self)
        WorkspaceHandler.pre_execution_hook(self)
        ValidatedHandler.pre_execution_hook(self)
    
    def post_execution_hook(self, log, output, usage_report, tool_logs):
        """Combined post-execution"""
        # Call all parent hooks
        ValidatedHandler.post_execution_hook(self, log, output, usage_report, tool_logs)
        WorkspaceHandler.post_execution_hook(self, log, output, usage_report, tool_logs)
        MonitoredHandler.post_execution_hook(self, log, output, usage_report, tool_logs)
```

## Best Practices

1. **Always call parent methods**: Use `super()` to ensure base functionality
2. **Handle errors gracefully**: Wrap operations in try-except blocks
3. **Document your extensions**: Add clear docstrings
4. **Keep it simple**: Don't over-engineer
5. **Test thoroughly**: Write unit tests for custom logic

## Next Steps

- See [complete examples](examples.md)
- Read the [API reference](../api-reference/common-execution-handler.md)
- Learn about [CustomStacIO](../api-reference/custom-stac-io.md)
