from uuid import uuid4

import pytest

from src.apis.auth import models, service as auth_service
from src.entities.models import User
from src.exceptions import AuthenticationError


class _Query:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._result


class _Db:
    def __init__(self, user=None):
        self.user = user
        self.added = []
        self.committed = False

    def query(self, model):
        return _Query(self.user if model is User else None)

    def add(self, value):
        self.added.append(value)

    def commit(self):
        self.committed = True

    def refresh(self, value):
        return None

    def rollback(self):
        return None


def test_password_hash_round_trip():
    hashed = auth_service.get_password_hash("password123")

    assert auth_service.verify_password("password123", hashed)
    assert not auth_service.verify_password("wrong", hashed)


def test_authenticate_user_success_and_failure():
    user = User(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash=auth_service.get_password_hash("password123"),
        is_active=True,
    )

    assert auth_service.authenticate_user("test@example.com", "password123", _Db(user)).email == user.email
    assert auth_service.authenticate_user("test@example.com", "bad", _Db(user)) is None


def test_inactive_user_is_rejected():
    user = User(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash=auth_service.get_password_hash("password123"),
        is_active=False,
    )

    with pytest.raises(AuthenticationError):
        auth_service.authenticate_user("test@example.com", "password123", _Db(user))


def test_register_user_persists_expected_fields():
    db = _Db()
    payload = models.RegisterUserRequest(
        email="new@example.com",
        full_name="New User",
        password="password123",
    )

    user = auth_service.register_user(db, payload)

    assert user.email == payload.email
    assert user.full_name == payload.full_name
    assert auth_service.verify_password(payload.password, user.password_hash)
    assert db.added == [user]
    assert db.committed


def test_access_token_verification_requires_expected_type():
    user_id = uuid4()
    session_id = uuid4()
    token = auth_service.create_access_token(
        "test@example.com",
        user_id,
        session_id,
        auth_service.timedelta(minutes=5),
    )

    token_data = auth_service.verify_token(token)

    assert token_data.get_uuid() == user_id
    assert token_data.get_session_uuid() == session_id
    with pytest.raises(AuthenticationError):
        auth_service.verify_token(token, expected_type="refresh")
