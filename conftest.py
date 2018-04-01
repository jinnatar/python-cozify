import pytest

def pytest_addoption(parser):
    parser.addoption("--live", action="store_true",
                     default=False, help="run tests requiring a functional auth and a real hub.")
    parser.addoption("--destructive", action="store_true",
                     default=False, help="run tests that require and modify the state of a real hub.")

def pytest_collection_modifyitems(config, items):
    live = False
    destructive = False
    if config.getoption("--live"):
        live = True
    if config.getoption("--destructive"):
        return
    skip_live = pytest.mark.skip(reason="need --live option to run")
    skip_destructive = pytest.mark.skip(reason="need --destructive option to run")
    
    for item in items:
        if "live" in item.keywords and not live:
            item.add_marker(skip_live)
        if "destructive" in item.keywords and not destructive:
            item.add_marker(skip_destructive)
