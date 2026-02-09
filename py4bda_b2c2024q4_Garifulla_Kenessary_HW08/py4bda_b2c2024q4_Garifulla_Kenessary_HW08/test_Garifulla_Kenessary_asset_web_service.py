import pytest
from task_Garifulla_Kenessary_asset_web_service import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_cbr_currency_base(client):
    response = client.get("/cbr/daily")
    assert response.status_code == 200
    assert "USD" in response.json

def test_cbr_key_indicators(client):
    response = client.get("/cbr/key_indicators")
    assert response.status_code == 200
    assert "USD" in response.json

def test_add_asset(client):
    # Add an asset first
    response = client.get("/api/asset/add/USD/Asset1/1000/0.05")
    assert response.status_code == 200
    assert "Asset 'Asset1' was successfully added" in response.data.decode()

    # Try adding the same asset again
    response = client.get("/api/asset/add/USD/Asset1/2000/0.05")
    assert response.status_code == 403
    assert "Asset 'Asset1' already exists" in response.data.decode()

def test_list_assets(client):
    # Add an asset first
    client.get("/api/asset/add/USD/Asset1/1000/0.05")
    response = client.get("/api/asset/list")
    assert response.status_code == 200
    assert len(response.json) > 0

def test_get_assets(client):
    # Add an asset first
    client.get("/api/asset/add/USD/Asset1/1000/0.05")
    response = client.get("/api/asset/get?name=Asset1")
    assert response.status_code == 200
    assert "Asset1" in [asset[1] for asset in response.json]

def test_calculate_revenue(client):
    # Add an asset first
    client.get("/api/asset/add/USD/Asset1/1000/0.05")
    response = client.get("/api/asset/calculate_revenue?period_1=0&period_2=1")
    assert response.status_code == 200
    assert "period_1" in response.json

def test_cleanup_assets(client):
    # Add an asset first
    client.get("/api/asset/add/USD/Asset1/1000/0.05")
    response = client.get("/api/asset/cleanup")
    assert response.status_code == 200
    assert "There are no more assets" in response.data.decode()

