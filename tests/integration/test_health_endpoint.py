"""
Integration tests for health check endpoints.
"""
import pytest


class TestHealthEndpoints:
    """Test health check and readiness endpoints."""
    
    def test_root_endpoint(self, test_client):
        """Test root endpoint returns correct response."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "PostBot" in data["message"]
        assert "version" in data
    
    def test_health_endpoint(self, test_client):
        """Test /health endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_readiness_endpoint(self, test_client):
        """Test /readiness endpoint checks dependencies."""
        response = test_client.get("/readiness")
        # May return 200 or 503 depending on dependencies
        assert response.status_code in [200, 503]
        data = response.json()
        assert "database" in data or "status" in data
    
    def test_liveness_endpoint(self, test_client):
        """Test /liveness endpoint."""
        response = test_client.get("/liveness")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "alive"
