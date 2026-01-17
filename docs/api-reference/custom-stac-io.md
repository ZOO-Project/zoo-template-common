# CustomStacIO API Reference

::: zoo_template_common.custom_stac_io.CustomStacIO
    options:
      show_source: true
      show_root_heading: true
      heading_level: 2

## Class Overview

`CustomStacIO` is a custom STAC I/O implementation that handles reading STAC items from S3 storage using boto3.

Extends `pystac.StacIO` to provide custom read/write operations for STAC catalogs stored in S3.

## Constructor

```python
def __init__(self)
```

Creates a new CustomStacIO instance with boto3 S3 client configured from environment variables.

**Environment Variables:**

- `AWS_ACCESS_KEY_ID`: S3 access key
- `AWS_SECRET_ACCESS_KEY`: S3 secret key  
- `AWS_S3_ENDPOINT`: S3 endpoint URL
- `AWS_DEFAULT_REGION`: AWS region (default: "us-east-1")

**Example:**

```python
from zoo_template_common import CustomStacIO

# Configure S3 environment
os.environ["AWS_ACCESS_KEY_ID"] = "..."
os.environ["AWS_SECRET_ACCESS_KEY"] = "..."
os.environ["AWS_S3_ENDPOINT"] = "https://s3.example.com"

# Create custom I/O
stac_io = CustomStacIO()
```

## Methods

### read_text()

Read text content from a file or S3 object.

```python
def read_text(self, source: str, *args, **kwargs) -> str
```

**Parameters:**

- `source` (str): File path or S3 URL (s3://bucket/key)
- `*args`: Additional positional arguments
- `**kwargs`: Additional keyword arguments

**Returns:**
- str: Text content from file or S3 object

**Behavior:**

- If `source` starts with "s3://", reads from S3 using boto3
- Otherwise, reads from local filesystem
- Parses S3 URL to extract bucket and key
- Returns decoded UTF-8 text

**Example:**

```python
# Read from S3
content = stac_io.read_text("s3://my-bucket/catalog.json")

# Read from local file
content = stac_io.read_text("/tmp/catalog.json")
```

### write_text()

Write text content to a file.

```python
def write_text(self, dest: str, txt: str, *args, **kwargs) -> None
```

**Parameters:**

- `dest` (str): Destination file path
- `txt` (str): Text content to write
- `*args`: Additional positional arguments
- `**kwargs`: Additional keyword arguments

**Behavior:**

- Creates parent directories if they don't exist
- Writes text to file using UTF-8 encoding

**Example:**

```python
import json

catalog_data = {"type": "Catalog", "id": "my-catalog"}
stac_io.write_text("/tmp/catalog.json", json.dumps(catalog_data))
```

### read_json()

Read and parse JSON from file or S3.

```python
def read_json(self, source: str, *args, **kwargs) -> dict
```

**Parameters:**

- `source` (str): File path or S3 URL

**Returns:**
- dict: Parsed JSON data

**Example:**

```python
catalog = stac_io.read_json("s3://bucket/catalog.json")
print(catalog["type"])  # "Catalog"
```

## Usage with PySTAC

### Set as Default STAC I/O

```python
from pystac import set_stac_io
from zoo_template_common import CustomStacIO

# Set as default for all PySTAC operations
set_stac_io(CustomStacIO())

# Now all PySTAC operations use CustomStacIO
from pystac import Catalog
catalog = Catalog.from_file("s3://bucket/catalog.json")
```

### Read STAC Catalog from S3

```python
from pystac import Catalog
from zoo_template_common import CustomStacIO
import os

# Configure S3
os.environ["AWS_ACCESS_KEY_ID"] = "your-key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "your-secret"
os.environ["AWS_S3_ENDPOINT"] = "https://s3.example.com"

# Set custom I/O
from pystac import set_stac_io
set_stac_io(CustomStacIO())

# Read catalog from S3
catalog = Catalog.from_file("s3://my-bucket/results/catalog.json")

# Iterate items
for item in catalog.get_items():
    print(f"Item: {item.id}")
    print(f"Assets: {list(item.assets.keys())}")
```

### Write STAC Catalog

```python
from pystac import Catalog, Item
from zoo_template_common import CustomStacIO
from pystac import set_stac_io

set_stac_io(CustomStacIO())

# Create catalog
catalog = Catalog(
    id="my-catalog",
    description="Processing results"
)

# Add items
item = Item(
    id="result-1",
    geometry=None,
    bbox=None,
    datetime=datetime.utcnow(),
    properties={}
)
catalog.add_item(item)

# Save to local filesystem
catalog.normalize_and_save("/tmp/output/catalog.json")
```

## S3 URL Format

CustomStacIO supports S3 URLs in the format:

```
s3://bucket-name/path/to/object
```

**Parsing:**

- Scheme: `s3://`
- Bucket: `bucket-name`
- Key: `path/to/object`

**Example URLs:**

```python
# Valid S3 URLs
"s3://my-bucket/catalog.json"
"s3://results/2024/01/15/output/catalog.json"
"s3://eoepca-data/workflows/job-123/results/catalog.json"
```

## Error Handling

```python
from botocore.exceptions import ClientError

try:
    content = stac_io.read_text("s3://bucket/catalog.json")
except ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchKey':
        print("Object not found")
    elif e.response['Error']['Code'] == 'NoSuchBucket':
        print("Bucket not found")
    else:
        print(f"S3 error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

## Configuration

### Environment Variables

Required for S3 access:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_S3_ENDPOINT="https://s3.example.com"
export AWS_DEFAULT_REGION="us-east-1"
```

### Boto3 Session

CustomStacIO creates a boto3 session with:

```python
session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
)
```

## Complete Example

```python
from zoo_template_common import CustomStacIO, CommonExecutionHandler
from pystac import set_stac_io, Catalog
import os

class MyHandler(CommonExecutionHandler):
    def pre_execution_hook(self):
        """Setup STAC I/O"""
        # Configure S3
        secrets = self.get_secrets()
        os.environ["AWS_ACCESS_KEY_ID"] = secrets["s3_key"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = secrets["s3_secret"]
        os.environ["AWS_S3_ENDPOINT"] = "https://s3.example.com"
        
        # Set custom STAC I/O
        set_stac_io(CustomStacIO())
    
    def post_execution_hook(self, log, output, usage_report, tool_logs):
        """Process STAC catalog from S3"""
        super().post_execution_hook(log, output, usage_report, tool_logs)
        
        # Read catalog from S3
        catalog_url = output.get("stac")
        if catalog_url and catalog_url.startswith("s3://"):
            catalog = Catalog.from_file(catalog_url)
            
            # Process items
            for item in catalog.get_items():
                print(f"Processing item: {item.id}")
```

## See Also

- [CommonExecutionHandler](common-execution-handler.md) - Main handler class
- [Basic Usage](../user-guide/basic-usage.md) - Usage examples
- [PySTAC Documentation](https://pystac.readthedocs.io/) - PySTAC library
