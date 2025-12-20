"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_generate_persona_endpoint(client):
    """Test persona generation endpoint."""
    payload = {
        "name": "Test Business",
        "location": "Pune, Maharashtra",
        "description": "Digital marketing company"
    }
    
    response = await client.post("/v1/personas/generate", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "job_id" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_get_persona(client):
    """Test get persona endpoint."""
    # First create a persona
    payload = {
        "name": "Test Business",
        "location": "Pune"
    }
    
    create_response = await client.post("/v1/personas/generate", json=payload)
    job_id = create_response.json()["job_id"]
    
    # Check job status
    status_response = await client.get(f"/v1/jobs/{job_id}")
    assert status_response.status_code == 200


@pytest.mark.asyncio
async def test_invalid_persona_request(client):
    """Test invalid persona request."""
    payload = {
        # Missing required fields
        "description": "Test"
    }
    
    response = await client.post("/v1/personas/generate", json=payload)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_nonexistent_persona(client):
    """Test getting non-existent persona."""
    response = await client.get("/v1/personas/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_submit_feedback(client):
    """Test feedback submission."""
    payload = {
        "persona_id": 1,
        "rating": 4,
        "comments": "Good persona",
        "corrections": {}
    }
    
    response = await client.post("/v1/feedback", json=payload)
    # May fail if persona doesn't exist, but endpoint should be accessible
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_concurrent_requests(client):
    """Test handling of concurrent requests."""
    import asyncio
    
    payload = {
        "name": f"Test Business",
        "location": "Pune"
    }
    
    # Submit multiple requests concurrently
    tasks = [
        client.post("/v1/personas/generate", json=payload)
        for _ in range(5)
    ]
    
    responses = await asyncio.gather(*tasks)
    
    # All should succeed
    assert all(r.status_code == 200 for r in responses)
    
    # All should have unique job IDs
    job_ids = [r.json()["job_id"] for r in responses]
    assert len(set(job_ids)) == 5
