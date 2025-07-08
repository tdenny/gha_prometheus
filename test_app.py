import pytest
import json
from app import app, extract_data_from_payload

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

def test_extract_data_from_payload():
    with open('sample_payload.json', 'r') as f:
        test_payload = json.load(f)
    extracted_data = extract_data_from_payload(test_payload)

    assert extracted_data["workflow_id"] == 1
    assert extracted_data["workflow_run_id"] == 30041
    assert extracted_data["conclusion"] == "success"
