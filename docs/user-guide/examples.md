# Complete Examples

This page provides real-world examples of using `zoo-template-common` from production templates.

## Example 1: Simple Handler (zoo-service-template)

The **zoo-service-template** (GeoLabs) shows a minimal extension of `CommonExecutionHandler`:

```python
from zoo_template_common import CommonExecutionHandler, CustomStacIO
from zoo_calrissian_runner import ZooCalrissianRunner
from pystac.stac_io import StacIO
import yaml
import os

# Set custom STAC I/O for S3 operations
StacIO.set_default(CustomStacIO)


class SimpleExecutionHandler(CommonExecutionHandler):
    """Simple execution handler for basic ZOO workflows.
    
    Extends CommonExecutionHandler with specific storage platform configuration.
    """

    def __init__(self, conf, outputs):
        super().__init__(conf, outputs)

    def get_additional_parameters(self):
        """Get additional parameters with eoap storage platform."""
        additional_parameters = super().get_additional_parameters()
        additional_parameters["storage_platform"] = "eoap"
        return additional_parameters


def my_workflow(conf, inputs, outputs):
    """ZOO Service entry point"""
    try:
        # Load CWL workflow
        with open("app-package.cwl", "r") as stream:
            cwl = yaml.safe_load(stream)

        # Create execution handler
        execution_handler = SimpleExecutionHandler(conf=conf, outputs=outputs)

        # Create runner
        runner = ZooCalrissianRunner(
            cwl=cwl,
            conf=conf,
            inputs=inputs,
            outputs=outputs,
            execution_handler=execution_handler,
        )

        # Execute workflow
        exit_status = runner.execute()
        return exit_status
        
    except Exception as e:
        conf["lenv"]["message"] = str(e)
        return 4  # SERVICE_FAILED
```

**Key points:**
- ✅ Only 15 lines of custom code (vs 250+ lines before using zoo-template-common)
- ✅ Adds single parameter: `storage_platform = "eoap"`
- ✅ Inherits all functionality: STAC processing, pod config, secrets handling
- ✅ Clean and maintainable

**Repository:** [GeoLabs/zoo-service-template](https://github.com/GeoLabs/zoo-service-template)

## Example 2: Advanced Handler with Workspace Integration (eoepca-proc-service-template)

The **eoepca-proc-service-template** shows a more complex extension with EOEPCA Workspace API integration:

```python
from zoo_template_common import CommonExecutionHandler, CustomStacIO
from zoo_calrissian_runner import ZooCalrissianRunner
import jwt
import requests
import os

class EoepcaCalrissianRunnerExecutionHandler(CommonExecutionHandler):
    """EOEPCA-specific execution handler with Workspace API integration."""

    def __init__(self, conf, outputs):
        super().__init__(conf, outputs)
        self.http_proxy_env = os.environ.get("HTTP_PROXY", None)
        self.username = None

        # Get auth environment
        auth_env = self.conf.get("auth_env", {})
        self.ades_rx_token = auth_env.get("jwt", "")

        # Get EOEPCA configuration
        eoepca = self.conf.get("eoepca", {})
        self.workspace_url = eoepca.get("workspace_url", "")
        self.workspace_prefix = eoepca.get("workspace_prefix", "")
        self.workspace_catalog_register = (
            eoepca.get("workspace_catalog_register", "false").lower() == "true"
        )

        # Initialize stage-in/stage-out defaults
        self.init_config_defaults(self.conf)

    @staticmethod
    def get_user_name(decodedJwt):
        """Extract username from JWT token."""
        for key in ["username", "user_name", "preferred_username"]:
            if key in decodedJwt:
                return decodedJwt[key]
        return None

    def pre_execution_hook(self):
        """Hook to run before execution with EOEPCA Workspace integration."""
        # Decode JWT token to get username
        if self.ades_rx_token:
            self.username = self.get_user_name(
                jwt.decode(self.ades_rx_token, options={"verify_signature": False})
            )

        # Lookup workspace storage details
        if self.workspace_url and self.username:
            workspace_api_endpoint = os.path.join(
                self.workspace_url,
                f"workspaces/{self.workspace_prefix}-{self.username}"
            )
            
            headers = {"accept": "application/json"}
            if self.ades_rx_token:
                headers["Authorization"] = f"Bearer {self.ades_rx_token}"

            response = requests.get(workspace_api_endpoint, headers=headers)

            if response.ok:
                workspace_data = response.json()
                storage_credentials = workspace_data["storage"]["credentials"]

                # Update stage-out configuration with user's workspace credentials
                self.conf["additional_parameters"].update({
                    "STAGEOUT_AWS_SERVICEURL": storage_credentials.get("endpoint"),
                    "STAGEOUT_AWS_ACCESS_KEY_ID": storage_credentials.get("access"),
                    "STAGEOUT_AWS_SECRET_ACCESS_KEY": storage_credentials.get("secret"),
                    "STAGEOUT_AWS_REGION": storage_credentials.get("region"),
                    "STAGEOUT_OUTPUT": workspace_data["storage"].get("buckets", {}).get("outputs")
                })

    def post_execution_hook(self, log, output, usage_report, tool_logs):
        """Process results and register to Workspace Catalogue."""
        # Call parent to setup S3 environment
        super().post_execution_hook(log, output, usage_report, tool_logs)

        # Register outputs to Workspace Catalogue if configured
        if self.workspace_catalog_register and self.username:
            self.register_to_workspace_catalogue(output)

    def register_to_workspace_catalogue(self, output):
        """Register STAC catalog to Workspace Catalogue."""
        stac_catalog_url = output.get("stac")
        if not stac_catalog_url:
            return

        register_endpoint = os.path.join(
            self.workspace_url,
            f"workspaces/{self.workspace_prefix}-{self.username}/register"
        )

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        if self.ades_rx_token:
            headers["Authorization"] = f"Bearer {self.ades_rx_token}"

        payload = {"stac_catalog_uri": stac_catalog_url}
        
        response = requests.post(register_endpoint, headers=headers, json=payload)
        if response.ok:
            logger.info("Successfully registered outputs to Workspace Catalogue")
        else:
            logger.warning(f"Failed to register outputs: {response.text}")


def my_workflow(conf, inputs, outputs):
    """ZOO Service with EOEPCA integration"""
    try:
        # Load CWL workflow
        with open("app-package.cwl", "r") as stream:
            cwl = yaml.safe_load(stream)

        # Create EOEPCA handler
        execution_handler = EoepcaCalrissianRunnerExecutionHandler(
            conf=conf, 
            outputs=outputs
        )

        # Create runner
        runner = ZooCalrissianRunner(
            cwl=cwl,
            conf=conf,
            inputs=inputs,
            outputs=outputs,
            execution_handler=execution_handler,
        )

        # Execute workflow
        exit_status = runner.execute()
        return exit_status
        
    except Exception as e:
        conf["lenv"]["message"] = str(e)
        return 4  # SERVICE_FAILED
```

**Key features:**
- ✅ JWT token authentication and user extraction
- ✅ Dynamic Workspace API integration for storage credentials
- ✅ Automatic stage-out to user's workspace bucket
- ✅ STAC catalog registration to Workspace Catalogue
- ✅ HTTP proxy management for network operations
- ✅ Fallback to environment variables for configuration

**Repository:** [EOEPCA/eoepca-proc-service-template](https://github.com/EOEPCA/eoepca-proc-service-template)

## Comparison: Simple vs Advanced

| Feature | SimpleExecutionHandler | EoepcaCalrissianRunnerExecutionHandler |
|---------|----------------------|----------------------------------------|
| **Lines of code** | ~15 | ~200 |
| **Code reduction** | 62% vs original | Still complex but organized |
| **Authentication** | None | JWT token decoding |
| **Storage** | Static configuration | Dynamic from Workspace API |
| **Catalog registration** | No | Yes, to Workspace Catalogue |
| **Use case** | Basic workflows | Multi-tenant EOEPCA platform |

## Running the Examples

### Prerequisites

```bash
# Install dependencies
pip install zoo-template-common
pip install zoo-calrissian-runner  # or zoo-argowf-runner, zoo-wes-runner
```

### Configuration

### Configuration

**For SimpleExecutionHandler (zoo-service-template):**

```python
conf = {
    "lenv": {
        "usid": "unique-execution-id",
        "Identifier": "my-workflow"
    },
    "main": {
        "tmpPath": "/tmp/zoo"
    },
    "additional_parameters": {
        # S3 configuration
        "aws_access_key_id": "ACCESS_KEY",
        "aws_secret_access_key": "SECRET_KEY",
        "endpoint_url": "https://s3.example.com",
        "region_name": "us-east-1"
    }
}
```

**For EoepcaCalrissianRunnerExecutionHandler (eoepca-proc-service-template):**

```python
conf = {
    "lenv": {
        "usid": "unique-execution-id",
        "Identifier": "my-workflow"
    },
    "main": {
        "tmpPath": "/tmp/zoo"
    },
    "auth_env": {
        "jwt": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."  # JWT token
    },
    "eoepca": {
        "domain": "demo.eoepca.org",
        "workspace_url": "https://workspace-api.demo.eoepca.org",
        "workspace_prefix": "ws",
        "workspace_catalog_register": "true"
    },
    "additional_parameters": {
        # Stage-in defaults
        "STAGEIN_AWS_SERVICEURL": "https://s3-stagein.example.com",
        "STAGEIN_AWS_ACCESS_KEY_ID": "STAGEIN_KEY",
        "STAGEIN_AWS_SECRET_ACCESS_KEY": "STAGEIN_SECRET",
        "STAGEIN_AWS_REGION": "us-east-1",
        
        # Stage-out will be overridden by Workspace API
        "STAGEOUT_AWS_SERVICEURL": "https://s3-stageout.example.com",
        "STAGEOUT_AWS_ACCESS_KEY_ID": "STAGEOUT_KEY",
        "STAGEOUT_AWS_SECRET_ACCESS_KEY": "STAGEOUT_SECRET",
        "STAGEOUT_AWS_REGION": "us-east-1",
        "STAGEOUT_OUTPUT": "workspace-bucket"
    }
}
```

## Architecture Diagrams

### SimpleExecutionHandler Flow

```
User Request
    ↓
SimpleExecutionHandler
    ├── get_additional_parameters() → Add "storage_platform"
    └── Inherit all from CommonExecutionHandler
        ├── STAC processing
        ├── Pod configuration
        └── S3 environment setup
    ↓
ZooCalrissianRunner
    ↓
Kubernetes Job (Calrissian)
    ↓
Results → STAC Catalog
```

### EoepcaCalrissianRunnerExecutionHandler Flow

```
User Request (with JWT)
    ↓
EoepcaCalrissianRunnerExecutionHandler
    ├── pre_execution_hook()
    │   ├── Decode JWT → Extract username
    │   ├── Call Workspace API → Get storage credentials
    │   └── Update stage-out configuration
    ├── Inherit STAC processing from CommonExecutionHandler
    └── post_execution_hook()
        ├── Setup S3 environment (parent)
        └── Register catalog to Workspace Catalogue
    ↓
ZooCalrissianRunner
    ↓
Kubernetes Job (Calrissian)
    ├── Stage-in from public S3
    └── Stage-out to user's workspace bucket
    ↓
Results → User's STAC Catalog → Registered in Workspace
```

## Best Practices from Real Templates

### 1. Keep Simple Handlers Simple

From **zoo-service-template**:
```python
# ✅ DO: Minimal override
class SimpleExecutionHandler(CommonExecutionHandler):
    def get_additional_parameters(self):
        params = super().get_additional_parameters()
        params["storage_platform"] = "eoap"
        return params

# ❌ DON'T: Reimplement everything
class BadHandler(CommonExecutionHandler):
    def __init__(self, conf, outputs):
        # Don't reimplement all the base logic
        pass
```

### 2. Use Hooks Appropriately

From **eoepca-proc-service-template**:
```python
# ✅ DO: Use pre_execution_hook for setup
def pre_execution_hook(self):
    self.username = self.extract_user_from_jwt()
    self.fetch_workspace_credentials()

# ✅ DO: Use post_execution_hook for finalization
def post_execution_hook(self, log, output, usage_report, tool_logs):
    super().post_execution_hook(log, output, usage_report, tool_logs)
    self.register_to_catalogue(output)

# ❌ DON'T: Put everything in __init__
```

### 3. Handle Secrets Securely

```python
# ✅ DO: Use get_secrets() method
def pre_execution_hook(self):
    secrets = self.get_secrets()
    api_key = secrets.get("api_key")

# ❌ DON'T: Hardcode credentials
```

### 4. Set Custom STAC I/O

Both templates use this pattern:
```python
from pystac.stac_io import StacIO
from zoo_template_common import CustomStacIO

# Set once at module level
StacIO.set_default(CustomStacIO)
```

## Testing Your Handler

### Unit Test Example

```python
import pytest
from your_service import SimpleExecutionHandler

def test_simple_handler():
    """Test SimpleExecutionHandler"""
    conf = {
        "lenv": {"message": ""},
        "additional_parameters": {}
    }
    outputs = {}
    
    handler = SimpleExecutionHandler(conf, outputs)
    params = handler.get_additional_parameters()
    
    assert "storage_platform" in params
    assert params["storage_platform"] == "eoap"

def test_eoepca_handler_jwt():
    """Test EOEPCA handler with JWT"""
    conf = {
        "lenv": {},
        "auth_env": {"jwt": "valid.jwt.token"},
        "eoepca": {
            "workspace_url": "https://workspace-api.example.com",
            "workspace_prefix": "ws"
        },
        "additional_parameters": {}
    }
    outputs = {}
    
    handler = EoepcaCalrissianRunnerExecutionHandler(conf, outputs)
    # Mock the requests.get call
    # Test that username is extracted correctly
    # Test that credentials are updated
```

## Additional Resources

- **zoo-service-template**: [github.com/GeoLabs/zoo-service-template](https://github.com/GeoLabs/zoo-service-template)
- **eoepca-proc-service-template**: [github.com/EOEPCA/eoepca-proc-service-template](https://github.com/EOEPCA/eoepca-proc-service-template)
- **Integration Guides**: See `INTEGRATION_ZOO_TEMPLATE_COMMON.md` and `TEMPLATE_INTEGRATION.md` in respective repositories

## Next Steps

- Review the [API Reference](../api-reference/common-execution-handler.md)
- Learn about [CustomStacIO](../api-reference/custom-stac-io.md)
- Read [Extending the Handler](extending.md) for more patterns
