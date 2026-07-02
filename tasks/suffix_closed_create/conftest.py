import importlib.util, os, pytest


def _load():
    spec = importlib.util.spec_from_file_location(
        "suffix_create_ref", os.path.join(os.path.dirname(__file__), "reference.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load()


@pytest.fixture
def suffix_closure():
    return _mod.suffix_closure


@pytest.fixture
def is_suffix_closed():
    return _mod.is_suffix_closed
