import copy
import os

import pytest

from zoo_template_common.common_execution_handler import CommonExecutionHandler

BASE_CONF = {
    "lenv": {"Identifier": "my-workflow", "usid": "test-456"},
    "main": {"tmpUrl": "http://example.com/temp/results"},
    "auth_env": {"user": "testuser"},
    "additional_parameters": {
        "region_name": "us-east-1",
        "endpoint_url": "http://s3.example.com",
    },
}


@pytest.fixture
def handler():
    return CommonExecutionHandler(
        conf=copy.deepcopy(BASE_CONF),
        outputs={"stac": {"mimeType": "application/geo+json", "value": None}},
    )


class TestLocalGetFile:
    def test_valid_yaml_file(self, tmp_path):
        f = tmp_path / "data.yaml"
        f.write_text("key: value\nnum: 42\n")
        result = CommonExecutionHandler.local_get_file(str(f))
        assert result == {"key": "value", "num": 42}

    def test_missing_file_returns_empty_dict(self):
        result = CommonExecutionHandler.local_get_file("/nonexistent/path/file.yaml")
        assert result == {}

    def test_empty_file_returns_empty_dict(self, tmp_path):
        f = tmp_path / "empty.yaml"
        f.write_text("")
        result = CommonExecutionHandler.local_get_file(str(f))
        assert result == {}

    def test_invalid_yaml_returns_empty_dict(self, tmp_path):
        f = tmp_path / "bad.yaml"
        f.write_text("key: [unclosed bracket\n")
        result = CommonExecutionHandler.local_get_file(str(f))
        assert result == {}


class TestGetAdditionalParameters:
    def test_includes_sub_path_equal_to_usid(self, handler):
        params = handler.get_additional_parameters()
        assert params["sub_path"] == "test-456"

    def test_includes_existing_parameters_from_conf(self, handler):
        params = handler.get_additional_parameters()
        assert params["region_name"] == "us-east-1"
        assert params["endpoint_url"] == "http://s3.example.com"

    def test_does_not_mutate_conf(self, handler):
        original = copy.deepcopy(handler.conf.get("additional_parameters", {}))
        handler.get_additional_parameters()
        assert handler.conf.get("additional_parameters", {}) == original

    def test_sub_path_not_persisted_in_conf(self, handler):
        handler.get_additional_parameters()
        assert "sub_path" not in handler.conf.get("additional_parameters", {})

    def test_returns_new_dict_each_call(self, handler):
        p1 = handler.get_additional_parameters()
        p2 = handler.get_additional_parameters()
        assert p1 is not p2


class TestGetPodEnvVars:
    def test_returns_pod_env_vars_from_conf(self):
        conf = {**copy.deepcopy(BASE_CONF), "pod_env_vars": {"MY_VAR": "value"}}
        h = CommonExecutionHandler(conf=conf, outputs={})
        assert h.get_pod_env_vars() == {"MY_VAR": "value"}

    def test_returns_empty_dict_when_absent(self, handler):
        assert handler.get_pod_env_vars() == {}


class TestGetPodNodeSelector:
    def test_returns_node_selector_from_conf(self):
        conf = {**copy.deepcopy(BASE_CONF), "pod_node_selector": {"gpu": "true"}}
        h = CommonExecutionHandler(conf=conf, outputs={})
        assert h.get_pod_node_selector() == {"gpu": "true"}

    def test_returns_empty_dict_when_absent(self, handler):
        assert handler.get_pod_node_selector() == {}


class TestGetSecrets:
    def test_returns_expected_keys(self, handler):
        secrets = handler.get_secrets()
        assert "imagePullSecrets" in secrets
        assert "additionalImagePullSecrets" in secrets

    def test_missing_secret_files_return_empty_dicts(self, handler):
        secrets = handler.get_secrets()
        assert secrets["imagePullSecrets"] == {}
        assert secrets["additionalImagePullSecrets"] == {}

    def test_reads_existing_secret_file(self, tmp_path):
        secret_file = tmp_path / "pod_imagePullSecrets.yaml"
        secret_file.write_text("registry: docker.io\n")

        original_get_file = CommonExecutionHandler.local_get_file

        def patched_get_file(filename):
            if filename == str(secret_file):
                return original_get_file(str(secret_file))
            return {}

        h = CommonExecutionHandler(conf=copy.deepcopy(BASE_CONF), outputs={})
        result = CommonExecutionHandler.local_get_file(str(secret_file))
        assert result == {"registry": "docker.io"}


class TestPreExecutionHook:
    def test_does_not_crash(self, handler):
        handler.pre_execution_hook()


class TestHandleOutputs:
    def test_creates_service_logs_from_tool_logs(self):
        conf = {
            "lenv": {"Identifier": "wf", "usid": "u1"},
            "main": {"tmpUrl": "http://example.com/temp/"},
            "auth_env": {"user": "alice"},
        }
        h = CommonExecutionHandler(conf=conf, outputs={})
        h.handle_outputs("log", {}, {}, ["/tmp/tool1.log", "/tmp/tool2.log"])
        assert "service_logs" in h.conf
        assert h.conf["service_logs"]["length"] == "2"

    def test_service_logs_url_includes_identifier_and_usid(self):
        conf = {
            "lenv": {"Identifier": "mywf", "usid": "abc"},
            "main": {"tmpUrl": "http://example.com/temp/"},
            "auth_env": {"user": "bob"},
        }
        h = CommonExecutionHandler(conf=conf, outputs={})
        h.handle_outputs("log", {}, {}, ["/tmp/step.log"])
        assert "mywf-abc" in h.conf["service_logs"]["url"]

    def test_handle_outputs_updates_tmp_url(self):
        conf = {
            "lenv": {"Identifier": "wf", "usid": "u1"},
            "main": {"tmpUrl": "http://example.com/temp/"},
            "auth_env": {"user": "carol"},
        }
        h = CommonExecutionHandler(conf=conf, outputs={})
        h.handle_outputs("log", {}, {}, [])
        assert "carol/temp/" in h.conf["main"]["tmpUrl"]

    def test_existing_service_logs_uses_indexed_keys(self):
        conf = {
            "lenv": {"Identifier": "wf", "usid": "u1"},
            "main": {"tmpUrl": "http://example.com/temp/"},
            "auth_env": {"user": "dave"},
            "service_logs": {"url": "existing", "title": "existing", "rel": "existing"},
        }
        h = CommonExecutionHandler(conf=conf, outputs={})
        h.handle_outputs("log", {}, {}, ["/tmp/new.log"])
        # When service_logs already exists, new entries get suffixed index
        assert "url_1" in h.conf["service_logs"]
