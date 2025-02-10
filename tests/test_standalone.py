import pytest
from worker_object_server.object_server import ObjectServer


def test_setitem():
    obj = ObjectServer()
    obj['key'] = 'value'
    assert obj['key'] == 'value'


def test_setitem_overwrite():
    obj =ObjectServer()
    obj['key'] = 'initial'
    obj['key'] = 'updated'
    assert obj['key'] == 'updated'


if __name__ == "__main__":
    pytest.main()
