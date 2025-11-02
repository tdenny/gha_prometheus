import json
import requests
from time import sleep

class PrometheusResponse:
    """
    Helper function to represent a response from a prometheus query.

    In the context of these tests, this class expects a single result object
    from prometheus queries. It also ignores the timestamp returned in the
    results.
    """

    def __init__(self, raw_response):
        self.status = raw_response['status']
        self.result_type = raw_response['data']['resultType']
        self.metric_name = raw_response['data']['result'][0]['metric']['__name__']
        self.metric_value = raw_response['data']['result'][0]['value'][1]

def send_test_payload(payload_file, payload_event):
    webhook_endpoint = 'http://localhost:8080/webhook'

    with open(payload_file, 'r') as f:
        test_payload = json.load(f)

    app_response = requests.post(webhook_endpoint,
                                 headers={'X-GitHub-Event': payload_event},
                                 json=test_payload)

    app_response.raise_for_status()

def query_prometheus(query):
    response = requests.get('http://localhost:9090/api/v1/query', params=query)

    response.raise_for_status()

    return PrometheusResponse(response.json())

def test_prometheus_scrapes_metrics():
    send_test_payload('tests/payloads/valid_workflow_run.json', 'workflow_run')
    send_test_payload('tests/payloads/valid_workflow_run_failed.json', 'workflow_run')
    send_test_payload('tests/payloads/valid_workflow_job.json', 'workflow_job')
    send_test_payload('tests/payloads/valid_workflow_job_failed.json', 'workflow_job')

    sleep(5)

    prom_query = {"query": 'githubactions_workflow_run_total{workflow_id="1"}'}
    prometheus_response = query_prometheus(prom_query)

    assert prometheus_response.metric_name == "githubactions_workflow_run_total"
    assert prometheus_response.metric_value == "2"

    prom_query = {"query": 'githubactions_workflow_run_success_total{workflow_id="1"}'}
    prometheus_response = query_prometheus(prom_query)

    assert prometheus_response.metric_name == "githubactions_workflow_run_success_total"
    assert prometheus_response.metric_value == "1"

    prom_query = {"query": 'githubactions_workflow_run_failure_total{workflow_id="1"}'}
    prometheus_response = query_prometheus(prom_query)

    assert prometheus_response.metric_name == "githubactions_workflow_run_failure_total"
    assert prometheus_response.metric_value == "1"

    prom_query = {"query": 'githubactions_workflow_job_total{workflow_run_id="30041"}'}
    prometheus_response = query_prometheus(prom_query)

    assert prometheus_response.metric_name == "githubactions_workflow_job_total"
    assert prometheus_response.metric_value == "2"

    prom_query = {"query": 'githubactions_workflow_job_success_total{workflow_run_id="30041"}'}
    prometheus_response = query_prometheus(prom_query)

    assert prometheus_response.metric_name == "githubactions_workflow_job_success_total"
    assert prometheus_response.metric_value == "1"

    prom_query = {"query": 'githubactions_workflow_job_failure_total{workflow_run_id="30041"}'}
    prometheus_response = query_prometheus(prom_query)

    assert prometheus_response.metric_name == "githubactions_workflow_job_failure_total"
    assert prometheus_response.metric_value == "1"
