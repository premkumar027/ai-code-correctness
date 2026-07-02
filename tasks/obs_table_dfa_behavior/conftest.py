import importlib.util, os, pytest


def _load():
    spec = importlib.util.spec_from_file_location(
        "obs_dfa_behavior_ref", os.path.join(os.path.dirname(__file__), "reference.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_mod = _load()


@pytest.fixture
def build_dfa():
    return _mod.build_dfa
