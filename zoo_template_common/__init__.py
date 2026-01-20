# zoo_template_common/__init__.py
from .common_execution_handler import CommonExecutionHandler
from .custom_stac_io import CustomStacIO

__all__ = ["CommonExecutionHandler", "CustomStacIO"]

try:
    from importlib.metadata import version
    __version__ = version("zoo-template-common")
except Exception:
    __version__ = "unknown"
