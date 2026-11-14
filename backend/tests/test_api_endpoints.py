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


@pytest.mark.asyncio
async def test_timeseries_downsample():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/timeseries?variable_id=t2m&max_points=24")
        assert response.status_code == 200
        data = response.json()
        assert data["downsampled"] is True
        assert data["summary"]["count"] == 300
        assert len(data["data"]) <= 26
        assert data["data"][0]["timestamp"] == "2001-01-01"


@pytest.mark.asyncio
async def test_get_variables_and_regions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        vars_res = await client.get("/api/v1/variables")
        assert vars_res.status_code == 200
        assert vars_res.json()["total_variables"] == 6

        regions_res = await client.get("/api/v1/regions")
        assert regions_res.status_code == 200
        payload = regions_res.json()
        assert payload["total_regions"] == 1
        assert payload["regions"][0]["id"] == "pakistan"


@pytest.mark.asyncio
async def test_invalid_variable_returns_400():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/timeseries?variable_id=not_a_variable")
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_anomaly_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/analysis/anomalies",
            json={"variable_id": "t2m", "top_n": 3},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["top_positive_anomalies"]) == 3
        assert len(data["top_negative_anomalies"]) == 3


@pytest.mark.asyncio
async def test_models_and_reports_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        models_res = await client.get("/api/v1/models")
        assert models_res.status_code == 200
        body = models_res.json()
        assert len(body["models"]) == 5

        reports_res = await client.get("/api/v1/reports")
        assert reports_res.status_code == 200
        assert len(reports_res.json()["reports"]) >= 4

        report = await client.get("/api/v1/reports/forecasting-methodology")
        assert report.status_code == 200
        assert "excerpt" in report.json()


@pytest.mark.asyncio
async def test_openapi_docs_available():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        docs = await client.get("/api/v1/docs")
        spec = await client.get("/api/v1/openapi.json")
        assert docs.status_code == 200
        assert spec.status_code == 200
        paths = spec.json()["paths"]
        assert "/api/v1/models" in paths
        assert "/api/v1/regions" in paths
        assert "/api/v1/variables" in paths
        assert "/api/v1/forecast" in paths
        assert "/api/v1/spatial/summary" in paths


@pytest.mark.asyncio
async def test_spatial_summary_endpoint():
    """Verify /api/v1/spatial/summary returns valid bounding box, zones, and FDR-corrected trends."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/spatial/summary")
        assert response.status_code == 200
        data = response.json()

        assert data["region_id"] == "pakistan"
        assert data["bounding_box"]["lat_min"] < data["bounding_box"]["lat_max"]
        assert len(data["zones"]) == 5
        assert len(data["variable_trends"]) == 6
        assert "Benjamini-Hochberg" in data["multiple_testing_correction"]

        # Check zone presence
        zone_ids = [z["id"] for z in data["zones"]]
        assert "northern_highlands" in zone_ids
        assert "upper_indus" in zone_ids
        assert "lower_indus" in zone_ids

