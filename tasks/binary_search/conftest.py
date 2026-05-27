import importlib.util, os, pytest

def _load():
    spec = importlib.util.spec_from_file_location(
        "binary_search_ref", os.path.join(os.path.dirname(__file__), "reference.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_mod = _load()

@pytest.fixture
def binary_search():
    return _mod.binary_search
