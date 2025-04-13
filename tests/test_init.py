"""
Tests for the pocketpp package initialization.
"""
import pytest


def test_import():
    """Test that the package can be imported."""
    import pocketpp
    assert pocketpp is not None


def test_version():
    """Test that the version is set correctly."""
    import pocketpp
    assert hasattr(pocketpp, "__version__")
    assert isinstance(pocketpp.version, str)
    assert pocketpp.__version__ == "0.1.0"


def test_author():
    """Test that the author is set correctly."""
    import pocketpp
    assert hasattr(pocketpp, "__author__")
    assert isinstance(pocketpp.__author__, str)

