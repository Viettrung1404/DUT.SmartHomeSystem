from src.apis.users.controller import admin_router, router


def test_users_router_exposes_current_profile_endpoint():
    paths = {route.path for route in router.routes}

    assert "/users/me" in paths


def test_admin_users_router_exposes_admin_management_endpoints():
    paths = {route.path for route in admin_router.routes}

    assert "/admin/users" in paths
    assert "/admin/users/{user_id}" in paths
    assert "/admin/users/{user_id}/deactivate" in paths
