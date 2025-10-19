import pytest
import json
from gha_prometheus.app import app
from gha_prometheus.app import calculate_workflow_duration
from gha_prometheus.app import validate_workflow_run_payload
from gha_prometheus.app import validate_workflow_job_payload
from gha_prometheus.app import BadRequestMissingField
from prometheus_client.parser import text_string_to_metric_families

@pytest.fixture()
def client():
    app.config.update({
        "TESTING": True,
        })
    return app.test_client()

def test_no_event_header(client):
    with open('tests/payloads/valid_workflow_run.json', 'r') as f:
        test_payload = json.load(f)
    response = client.post('/webhook',
                           json=test_payload,
                           content_type='application/json')

    assert response.status_code == 400
    assert response.json['message'] == 'Missing X-GitHub-Event header'

def test_no_payload(client):
    response = client.post('/webhook',
                           content_type='application/json',
                           headers={'X-GitHub-Event': 'workflow_run'})
    assert response.status_code == 400

def test_payload_not_json(client):
    response = client.post('/webhook',
                           data="Non-json payload",
                           content_type='text/plain',
                           headers={'X-GitHub-Event': 'workflow_run'})
    response_data = response.get_data()

    assert response.status_code == 415
    assert b"Unsupported Media Type" in response_data

def test_validate_workflow_run_payload_success():
    with open('tests/payloads/valid_workflow_run.json', 'r') as f:
        test_payload = json.load(f)

    assert validate_workflow_run_payload(test_payload) is None

def test_validate_workflow_run_payload_failure():
    with open('tests/payloads/invalid_workflow_run.json', 'r') as f:
        test_payload = json.load(f)

    with pytest.raises(BadRequestMissingField):
        validate_workflow_run_payload(test_payload)

def test_validate_workflow_job_payload_success():
    with open('tests/payloads/valid_workflow_job.json', 'r') as f:
        test_payload = json.load(f)

    assert validate_workflow_job_payload(test_payload) is None

def test_validate_workflow_job_payload_failure():
    with open('tests/payloads/invalid_workflow_job.json', 'r') as f:
        test_payload = json.load(f)

    with pytest.raises(BadRequestMissingField):
        validate_workflow_job_payload(test_payload)

def test_calculate_duration():
    with open('tests/payloads/valid_workflow_run.json', 'r') as f:
        test_payload = json.load(f)

    assert calculate_workflow_duration(test_payload) == 19

def test_workflow_run_metrics_recorded(client):
    with open('tests/payloads/valid_workflow_run.json', 'r') as f:
        test_payload = json.load(f)
    response = client.post('/webhook',
                           json=test_payload,
                           content_type='application/json',
                           headers={'X-GitHub-Event': 'workflow_run'})

    assert response.status_code == 200

    response = client.get('/metrics')

    metric_families = text_string_to_metric_families(response.get_data(as_text=True))
    metric_names = []
    for metric in metric_families:
        metric_names.append(metric.name)

    # Note prometheus_client strips the 'total' suffix from the metric name
    assert "githubactions_workflow_run" in metric_names
    assert "githubactions_workflow_run_duration_seconds" in metric_names

def test_workflow_job_metrics_recorded(client):
    with open('tests/payloads/valid_workflow_job.json', 'r') as f:
        test_payload = json.load(f)
    response = client.post('/webhook',
                           json=test_payload,
                           content_type='application/json',
                           headers={'X-GitHub-Event': 'workflow_job'})

    assert response.status_code == 200

    response = client.get('/metrics')

    metric_families = text_string_to_metric_families(response.get_data(as_text=True))
    metric_names = []
    for metric in metric_families:
        metric_names.append(metric.name)

    # Note prometheus_client strips the 'total' suffix from the metric name
    assert "githubactions_workflow_job" in metric_names
    assert "githubactions_workflow_job_success" in metric_names

def test_invalid_workflow_run_payload(client):
    with open('tests/payloads/invalid_workflow_run.json', 'r') as f:
        invalid_payload = json.load(f)
    response = client.post('/webhook',
                           json=invalid_payload,
                           content_type='application/json',
                           headers={'X-GitHub-Event': 'workflow_run'})

    assert response.status_code == 400
    assert response.json["message"] == "Invalid request payload"
    assert response.json["errors"] == [{"field": "workflow_run",
                                        "message": "Field 'workflow_run' is required."}]

def test_invalid_workflow_job_payload(client):
    with open('tests/payloads/invalid_workflow_job.json', 'r') as f:
        invalid_payload = json.load(f)
    response = client.post('/webhook',
                           json=invalid_payload,
                           content_type='application/json',
                           headers={'X-GitHub-Event': 'workflow_job'})

    assert response.status_code == 400
    assert response.json["message"] == "Invalid request payload"
    assert response.json["errors"] == [{"field": "workflow_job",
                                        "message": "Field 'workflow_job' is required."}]
