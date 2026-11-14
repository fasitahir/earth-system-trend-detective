"""API endpoints integration tests."""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_get_datasets_endpoint():
    """Verify /api/v1/datasets returns valid catalog with 6 variables."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/datasets")
        assert response.status_code == 200
        data = response.json()
        assert data["total_variables"] == 6
        assert len(data["datasets"]) > 0

        # Check variable presence
        all_var_ids = [v["id"] for d in data["datasets"] for v in d["variables"]]
        assert "t2m" in all_var_ids
        assert "precipitation" in all_var_ids
        assert "soil_moisture_0_10cm" in all_var_ids


@pytest.mark.asyncio
async def test_get_timeseries_endpoint():
    """Verify /api/v1/timeseries returns canonical observation records."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/timeseries?variable_id=t2m")
        assert response.status_code == 200
        data = response.json()
        assert data["variable_id"] == "t2m"
        assert data["display_unit"] == "°C"
        assert data["region"] == "Pakistan"
        assert len(data["data"]) == 300
        assert data["summary"]["count"] == 300
        assert data["summary"]["min"] < data["summary"]["max"]

        # First observation check
        first_pt = data["data"][0]
        assert first_pt["timestamp"] == "2001-01-01"
        assert first_pt["display_value"] is not None
        assert first_pt["anomaly"] is not None


@pytest.mark.asyncio
async def test_get_timeseries_with_filter():
    """Verify date range filtering works properly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/timeseries?variable_id=precipitation&start_date=2020-01-01&end_date=2020-12-31"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 12
        assert data["start_date"] == "2020-01-01"
        assert data["end_date"] == "2020-12-01"
