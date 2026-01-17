# common/common_execution_handler.py

import json
import os
import traceback

import yaml
from loguru import logger
from pystac import Catalog, Collection, read_file
from pystac.item_collection import ItemCollection
from pystac.stac_io import StacIO


class CommonExecutionHandler:
    """Simple execution handler for ZOO-Project CWL workflows.

    This class provides basic functionality for handling CWL workflow execution
    with STAC catalog output processing. For more specific use cases (e.g., EOEPCA
    with Workspace API integration), extend this class and override the hooks.
    """

    def __init__(self, conf, outputs=None):
        self.conf = conf
        self.outputs = outputs or {}
        self.results = None

    def pre_execution_hook(self):
        """Hook to run before execution. Override in subclasses for custom behavior."""
        logger.info("Pre execution hook")

    def setOutput(self, outputName, values):
        """Process and set output values from STAC catalog."""
        output = self.outputs[outputName]
        logger.info(f"Read catalog from STAC Catalog URI: {output} -> {values}")

        if not isinstance(values[outputName], list):
            logger.info(f"values[{outputName}] is not a list, transform to an array")
            values[outputName] = [values[outputName]]

        items = []

        for i in range(len(values[outputName])):
            if values[outputName][i] is None:
                break
            cat: Catalog = read_file(values[outputName][i]["value"])

            collection_id = self.get_additional_parameters()["sub_path"]
            logger.info(f"Create collection with ID {collection_id}")

            collection = None

            try:
                logger.info(f"Catalog : {dir(cat)}")
                collection: Collection = next(cat.get_all_collections())
            except Exception:
                logger.error("No collection found in the output catalog")
                output["collection"] = json.dumps({}, indent=2)
                return

            logger.info(f"Got collection {collection.id} from processing outputs")

            for item in collection.get_all_items():
                logger.info(f"Processing item {item.id}")

                for asset_key in item.assets.keys():
                    logger.info(f"Processing asset {asset_key}")

                    temp_asset = item.assets[asset_key].to_dict()
                    temp_asset["storage:platform"] = self.get_additional_parameters().get(
                        "storage_platform", "default"
                    )
                    temp_asset["storage:requester_pays"] = False
                    temp_asset["storage:tier"] = "Standard"
                    temp_asset["storage:region"] = self.get_additional_parameters().get(
                        "region_name", "default"
                    )
                    temp_asset["storage:endpoint"] = self.get_additional_parameters().get(
                        "endpoint_url", ""
                    )
                    item.assets[asset_key] = item.assets[asset_key].from_dict(temp_asset)

                item.collection_id = collection_id
                items.append(item.clone())

        item_collection = ItemCollection(items=items)
        logger.info("Created feature collection from items")

        # Trap the case of no output collection
        if item_collection is None:
            logger.error("The output collection is empty")
            output["collection"] = json.dumps({}, indent=2)
            return

        # Set the feature collection to be returned
        output["collection"] = item_collection.to_dict()
        output["collection"]["id"] = collection_id

    def post_execution_hook(self, log, output, usage_report, tool_logs):
        """Hook to run after execution. Sets up S3 environment and processes outputs."""
        # Unset HTTP proxy or else the S3 client will use it and fail
        os.environ.pop("HTTP_PROXY", None)

        # Set S3 environment variables from additional parameters
        additional_params = self.get_additional_parameters()
        os.environ["AWS_S3_REGION"] = additional_params.get("region_name", "")
        os.environ["AWS_S3_ENDPOINT"] = additional_params.get("endpoint_url", "")
        os.environ["AWS_ACCESS_KEY_ID"] = additional_params.get("aws_access_key_id", "")
        os.environ["AWS_SECRET_ACCESS_KEY"] = additional_params.get("aws_secret_access_key", "")

        logger.info("Post execution hook")

        from zoo_template_common.custom_stac_io import CustomStacIO

        StacIO.set_default(CustomStacIO)

        for i in self.outputs:
            logger.info(f"Output {i}: {self.outputs[i]}")
            if "mimeType" in self.outputs[i]:
                self.setOutput(i, output)
            else:
                logger.warning(f"Output {i} has no mimeType, skipping...")
                self.outputs[i]["value"] = str(output[i])

    @staticmethod
    def local_get_file(fileName):
        """Read and load the contents of a yaml file."""
        try:
            with open(fileName) as file:
                data = yaml.safe_load(file)
            return data
        except (FileNotFoundError, yaml.YAMLError, yaml.scanner.ScannerError):
            return {}

    def get_pod_env_vars(self) -> dict[str, str]:
        """Get environment variables for the pod spawned by calrissian."""
        logger.info("get_pod_env_vars")
        return self.conf.get("pod_env_vars", {})

    def get_pod_node_selector(self) -> dict[str, str]:
        """Get node selector for the pod spawned by calrissian."""
        logger.info("get_pod_node_selector")
        return self.conf.get("pod_node_selector", {})

    def get_additional_parameters(self) -> dict[str, str]:
        """Get additional parameters for the execution."""
        logger.info("get_additional_parameters")
        additional_parameters = self.conf.get("additional_parameters", {})
        additional_parameters["sub_path"] = self.conf["lenv"]["usid"]
        return additional_parameters

    def get_secrets(self):
        """Get secrets for the pod spawned by calrissian."""
        logger.info("get_secrets")
        secrets = {
            "imagePullSecrets": self.local_get_file("/assets/pod_imagePullSecrets.yaml"),
            "additionalImagePullSecrets": self.local_get_file(
                "/assets/pod_additionalImagePullSecrets.yaml"
            ),
        }
        return secrets

    def handle_outputs(self, log, output, usage_report, tool_logs):
        """Handle the output files of the execution and register tool logs."""
        try:
            logger.info("handle_outputs")

            # Update tmpUrl with user path
            self.conf["main"]["tmpUrl"] = self.conf["main"]["tmpUrl"].replace(
                "temp/", self.conf["auth_env"]["user"] + "/temp/"
            )

            # Create service logs entries
            services_logs = [
                {
                    "url": os.path.join(
                        self.conf["main"]["tmpUrl"],
                        f"{self.conf['lenv']['Identifier']}-{self.conf['lenv']['usid']}",
                        os.path.basename(tool_log),
                    ),
                    "title": f"Tool log {os.path.basename(tool_log)}",
                    "rel": "related",
                }
                for tool_log in tool_logs
            ]

            cindex = 0
            if "service_logs" in self.conf:
                cindex = 1

            for i in range(len(services_logs)):
                okeys = ["url", "title", "rel"]
                keys = ["url", "title", "rel"]
                if cindex > 0:
                    for j in range(len(keys)):
                        keys[j] = keys[j] + "_" + str(cindex)
                if "service_logs" not in self.conf:
                    self.conf["service_logs"] = {}
                for j in range(len(keys)):
                    self.conf["service_logs"][keys[j]] = services_logs[i][okeys[j]]
                cindex += 1
                logger.warning(f"service_logs: {self.conf['service_logs']}")

            self.conf["service_logs"]["length"] = str(cindex)
            logger.info(f"service_logs: {self.conf['service_logs']}")

        except Exception as e:
            logger.error("ERROR in handle_outputs...")
            logger.error(traceback.format_exc())
            raise (e)
