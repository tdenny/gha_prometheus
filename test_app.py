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
    response_data = response.get_data()

    assert response.status_code == 415
    assert b"Unsupported Media Type" in response_data
