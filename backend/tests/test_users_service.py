from uuid import uuid4

import pytest

from src.apis.users import models, service as users_service
from src.entities.models import User
from src.exceptions import UserNotFoundError


class _Query:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self._result

    def all(self):
        return [self._result] if self._result else []


class _Db:
    def __init__(self, user=None):
        self.user = user
        self.added = []
        self.deleted = []
        self.committed = False

    def query(self, model):
        return _Query(self.user if model is User else None)

    def add(self, value):
        self.added.append(value)

    def delete(self, value):
        self.deleted.append(value)

    def commit(self):
        self.committed = True

    def refresh(self, value):
        return None


def test_get_user_by_id_returns_user_or_raises():
    user = User(id=uuid4(), email="user@example.com", full_name="User")

    assert users_service.get_user_by_id(_Db(user), user.id) is user
    with pytest.raises(UserNotFoundError):
        users_service.get_user_by_id(_Db(), uuid4())


def test_admin_create_user_hashes_password():
    db = _Db()
    payload = models.AdminCreateUserRequest(
        email="admin-created@example.com",
        full_name="Created User",
        password="password123",
        role="MEMBER",
        is_active=True,
    )

    user = users_service.create_user_by_admin(db, payload)

    assert user.email == payload.email
    assert user.full_name == payload.full_name
    assert user.password_hash != payload.password
    assert db.added == [user]
    assert db.committed


def test_admin_update_and_delete_user():
    user = User(id=uuid4(), email="user@example.com", full_name="Old", role="MEMBER", is_active=True)
    db = _Db(user)

    updated = users_service.update_user_by_admin(
        db,
        user.id,
        models.AdminUpdateUserRequest(full_name="New", is_active=False),
    )

    assert updated.full_name == "New"
    assert updated.is_active is False
    users_service.delete_user_by_admin(db, user.id)
    assert db.deleted == [user]
