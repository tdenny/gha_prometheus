import pytest
from app import app

@pytest.fixture()
def client():
    app.config.update({
        "TESTING": True,
        })
    return app.test_client()

def test_payload_not_json(client):
    response = client.post('/webhook',
                           data="Non-json payload",
                           content_type='text/plain')
    response_data = response.get_json()

    assert response.status_code == 400
    assert response_data["status"] == "error"
    assert response_data["message"] == "Request must be JSON"
