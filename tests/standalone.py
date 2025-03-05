import pytest

from worker_object_server.object_server import ObjectServer


class TestObjectServer:
    def setup_method(self):
        self.obj = ObjectServer()

    def teardown_method(self):
        self.obj.stop()

    def test_setitem(self):
        self.obj["key"] = "value"
        assert self.obj["key"] == "value"

    def test_setitem_overwrite(self):
        self.obj["key"] = "initial"
        self.obj["key"] = "updated"
        assert self.obj["key"] == "updated"


if __name__ == "__main__":
    pytest.main()
