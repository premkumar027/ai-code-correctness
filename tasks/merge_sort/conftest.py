import importlib.util, os, pytest

def _load():
    spec = importlib.util.spec_from_file_location(
        "merge_sort_ref", os.path.join(os.path.dirname(__file__), "reference.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_mod = _load()

@pytest.fixture
def merge():
    return _mod.merge

@pytest.fixture
def merge_sort():
    return _mod.merge_sort
