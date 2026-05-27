import importlib.util, os, pytest

def _load():
    spec = importlib.util.spec_from_file_location(
        "closedness_check_ref", os.path.join(os.path.dirname(__file__), "reference.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_mod = _load()

@pytest.fixture
def is_closed():
    return _mod.is_closed
