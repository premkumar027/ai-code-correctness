import importlib.util, os, pytest


def _load():
    spec = importlib.util.spec_from_file_location(
        "obs_consistent_ref", os.path.join(os.path.dirname(__file__), "reference.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load()


@pytest.fixture
def is_consistent():
    return _mod.is_consistent


@pytest.fixture
def make_consistent():
    return _mod.make_consistent
