import sys
from pathlib import Path

# Add the application directory to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Import the Flask application
from app import app


def test_health_endpoint():
    # Create a test client for the Flask application
    client = app.test_client()

    # Send a GET request to the health endpoint
    response = client.get("/health")

    # Verify the response
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_home_endpoint():
    # Create a test client
    client = app.test_client()

    # Send a GET request to the home page
    response = client.get("/")

    # Verify the response
    assert response.status_code == 200
    assert b"AWS Cloud Operations Dashboard" in response.data