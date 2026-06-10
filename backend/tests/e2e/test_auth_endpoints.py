from src.apis.auth.controller import router


def test_auth_router_exposes_current_endpoints():
    paths = {route.path for route in router.routes}

    assert "/auth/register" in paths
    assert "/auth/login" in paths
    assert "/auth/login-json" in paths
    assert "/auth/refresh" in paths
    assert "/auth/me" in paths
