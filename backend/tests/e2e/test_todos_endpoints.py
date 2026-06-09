from src.main import app


def test_legacy_todos_endpoints_are_not_registered():
    paths = {route.path for route in app.routes}

    assert "/todos/" not in paths
