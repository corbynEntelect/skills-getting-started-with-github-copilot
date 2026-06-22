"""Pytest configuration and shared fixtures for FastAPI tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app.
    
    This fixture creates a fresh TestClient for each test,
    ensuring test isolation and reproducibility.
    """
    return TestClient(app)
