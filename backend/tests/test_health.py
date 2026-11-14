"""Health endpoint tests."""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Verify health endpoint returns 200 OK and expected structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["project_name"] == "EarthScope API"
        assert "version" in data
        assert "environment" in data
        assert "timestamp" in data
        assert "components" in data
        assert data["components"]["api"] == "operational"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Verify root endpoint returns service info."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data
