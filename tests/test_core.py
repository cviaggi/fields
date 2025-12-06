"""Tests for the core module."""

import pytest

from fields.core import Field


class TestField:
    """Test cases for the Field class."""

    def test_field_creation(self):
        """Test creating a field."""
        field = Field("test_field", "test_value")
        assert field.name == "test_field"
        assert field.value == "test_value"

    def test_field_repr(self):
        """Test field string representation."""
        field = Field("name", 42)
        assert repr(field) == "Field(name='name', value=42)"
