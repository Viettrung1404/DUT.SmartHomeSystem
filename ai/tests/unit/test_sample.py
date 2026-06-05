"""
Sample unit test to verify test infrastructure is working.
This file can be removed once actual tests are implemented.
"""

import pytest


def test_sample_addition():
    """Sample test to verify pytest is working."""
    assert 1 + 1 == 2


def test_sample_string():
    """Sample test for string operations."""
    text = "Hello, World!"
    assert text.lower() == "hello, world!"
    assert len(text) == 13


@pytest.mark.unit
def test_sample_with_marker():
    """Sample test with unit marker."""
    result = [1, 2, 3, 4, 5]
    assert len(result) == 5
    assert sum(result) == 15
