from unittest import mock

import pytest

import proxmoxer.core as core

# pylint: disable=no-self-use


class TestResourceException:
    def test_init_none(self):
        e = core.ResourceException(None, None, None)

        assert e.status_code is None
        assert e.status_message is None
        assert e.content is None
        assert e.errors is None
        assert str(e) == "None None: None"

    def test_init_basic(self):
        e = core.ResourceException(500, "Internal Error", "Unable to do the thing")

        assert e.status_code == 500
        assert e.status_message == "Internal Error"
        assert e.content == "Unable to do the thing"
        assert e.errors is None
        assert str(e) == "500 Internal Error: Unable to do the thing"

    def test_init_error(self):
        e = core.ResourceException(
            500, "Internal Error", "Unable to do the thing", "functionality not found"
        )

        assert e.status_code == 500
        assert e.status_message == "Internal Error"
        assert e.content == "Unable to do the thing"
        assert e.errors == "functionality not found"
        assert str(e) == "500 Internal Error: Unable to do the thing - functionality not found"


class TestProxmoxResource:
    obj = core.ProxmoxResource()

    def test_url_join_empty_base(self):
        assert "/" == self.obj.url_join("", "")

    def test_url_join_empty(self):
        assert "https://www.example.com:80/" == self.obj.url_join("https://www.example.com:80", "")

    def test_url_join_basic(self):
        assert "https://www.example.com/nodes/node1" == self.obj.url_join(
            "https://www.example.com", "nodes", "node1"
        )

    def test_url_join_all_segments(self):
        assert "https://www.example.com/base/path#div1?search=query" == self.obj.url_join(
            "https://www.example.com/base#div1?search=query", "path"
        )

    def test_getattr_private(self):
        with pytest.raises(AttributeError) as exc_info:
            self.obj._thing

        print(exc_info)
        assert str(exc_info.value) == "_thing"

    def test_getattr_single(self, add_get_store):
        test_obj = core.ProxmoxResource(base_url="http://example.com/")
        ret = test_obj.nodes

        assert isinstance(ret, core.ProxmoxResource)
        assert ret.get_store()["base_url"] == "http://example.com/nodes"

    def test_call_basic(self, add_get_store):
        test_obj = core.ProxmoxResource(base_url="http://example.com/")
        ret = test_obj("nodes")

        assert isinstance(ret, core.ProxmoxResource)
        assert ret.get_store()["base_url"] == "http://example.com/nodes"

    def test_call_emptystr(self, add_get_store):
        test_obj = core.ProxmoxResource(base_url="http://example.com/")
        ret = test_obj("")

        assert isinstance(ret, core.ProxmoxResource)
        assert ret.get_store()["base_url"] == "http://example.com/"


class ProxmoxResourceWrapper(core.ProxmoxResource):
    def get_store(self):
        return self._store


@pytest.fixture
def add_get_store():
    with mock.patch("proxmoxer.core.ProxmoxResource", ProxmoxResourceWrapper):
        yield
