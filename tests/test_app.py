import pytest
import json
from gha_prometheus.app import app, extract_data_from_payload
from prometheus_client.parser import text_string_to_metric_families

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
    with open('tests/sample_payload.json', 'r') as f:
        test_payload = json.load(f)
    extracted_data = extract_data_from_payload(test_payload)

    assert extracted_data["workflow_id"] == 1
    assert extracted_data["workflow_run_id"] == 30041
    assert extracted_data["conclusion"] == "success"

def test_metrics_recorded(client):
    with open('tests/sample_payload.json', 'r') as f:
        test_payload = json.load(f)
    response = client.post('/webhook',
                           json=test_payload,
                           content_type='application/json')

    assert response.status_code == 200

    response = client.get('/metrics')

    metric_families = text_string_to_metric_families(response.get_data(as_text=True))
    metric_names = []
    for metric in metric_families:
        metric_names.append(metric.name)

    # Note prometheus_client strips the 'total' suffix from the metric name
    assert "githubactions_workflow_run" in metric_names

def test_invalid_payload(client):
    with open('tests/invalid_payload.json', 'r') as f:
        invalid_payload = json.load(f)
    response = client.post('/webhook',
                           json=invalid_payload,
                           content_type='application/json')

    assert response.status_code == 400
    assert response.json["message"] == "Invalid request payload"
    assert response.json["errors"] == [{"field": "workflow_run",
                                        "message": "Field 'workflow_run' is required."}]
