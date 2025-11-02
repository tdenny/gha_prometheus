import json
import requests
from deepdiff import DeepDiff
from time import sleep

def send_test_payload(payload_file, payload_event):
    webhook_endpoint = 'http://localhost:8080/webhook'

    with open(payload_file, 'r') as f:
        test_payload = json.load(f)

    app_response = requests.post(webhook_endpoint,
                                 headers={'X-GitHub-Event': payload_event},
                                 json=test_payload)

    app_response.raise_for_status()

def test_prometheus_scrapes_metrics():
    send_test_payload('tests/payloads/valid_workflow_run.json', 'workflow_run')
    send_test_payload('tests/payloads/valid_workflow_run_failed.json', 'workflow_run')
    send_test_payload('tests/payloads/valid_workflow_job.json', 'workflow_job')
    send_test_payload('tests/payloads/valid_workflow_job_failed.json', 'workflow_job')

    sleep(5)

    prom_query = {"query": 'githubactions_workflow_run_total{workflow_id="1"}'}
    expected_query_result = {
                              "status": "success",
                              "data": {
                                "resultType": "vector",
                                "result": [
                                  {
                                    "metric": {
                                      "__name__": "githubactions_workflow_run_total",
                                      "instance": "gha_prometheus:80",
                                      "job": "gha_prometheus",
                                      "workflow_id": "1"
                                    },
                                    "value": [
                                      1753968692.312,
                                      "2"
                                    ]
                                  }
                                ]
                              }
                            }

    prometheus_response = requests.get('http://localhost:9090/api/v1/query',
                                       params=prom_query)

    assert {} == DeepDiff(prometheus_response.json(),
                          expected_query_result,
                          exclude_paths=["root['data']['result'][0]['value'][0]"])

    prom_query = {"query": 'githubactions_workflow_run_success_total{workflow_id="1"}'}
    expected_query_result = {
                              "status": "success",
                              "data": {
                                "resultType": "vector",
                                "result": [
                                  {
                                    "metric": {
                                      "__name__": "githubactions_workflow_success_total",
                                      "instance": "gha_prometheus:80",
                                      "job": "gha_prometheus",
                                      "workflow_id": "1"
                                    },
                                    "value": [
                                      1753968692.312,
                                      "1"
                                    ]
                                  }
                                ]
                              }
                            }

    prometheus_response = requests.get('http://localhost:9090/api/v1/query',
                                       params=prom_query)

    assert {} == DeepDiff(prometheus_response.json(),
                          expected_query_result,
                          exclude_paths=["root['data']['result'][0]['value'][0]"])

    prom_query = {"query": 'githubactions_workflow_run_failure_total{workflow_id="1"}'}
    expected_query_result = {
                              "status": "success",
                              "data": {
                                "resultType": "vector",
                                "result": [
                                  {
                                    "metric": {
                                      "__name__": "githubactions_workflow_failure_total",
                                      "instance": "gha_prometheus:80",
                                      "job": "gha_prometheus",
                                      "workflow_id": "1"
                                    },
                                    "value": [
                                      1753968692.312,
                                      "1"
                                    ]
                                  }
                                ]
                              }
                            }

    prometheus_response = requests.get('http://localhost:9090/api/v1/query',
                                       params=prom_query)

    assert {} == DeepDiff(prometheus_response.json(),
                          expected_query_result,
                          exclude_paths=["root['data']['result'][0]['value'][0]"])

    prom_query = {"query": 'githubactions_workflow_job_total{workflow_run_id="30041"}'}
    expected_query_result = {
                              "status": "success",
                              "data": {
                                "resultType": "vector",
                                "result": [
                                  {
                                    "metric": {
                                      "__name__": "githubactions_workflow_job_total",
                                      "instance": "gha_prometheus:80",
                                      "job": "gha_prometheus",
                                      "workflow_job_id": "48831014846",
                                      "workflow_run_id": "30041"
                                    },
                                    "value": [
                                      1753968692.312,
                                      "2"
                                    ]
                                  }
                                ]
                              }
                            }

    prometheus_response = requests.get('http://localhost:9090/api/v1/query',
                                       params=prom_query)

    assert {} == DeepDiff(prometheus_response.json(),
                          expected_query_result,
                          exclude_paths=["root['data']['result'][0]['value'][0]"])

    prom_query = {"query": 'githubactions_workflow_job_success_total{workflow_run_id="30041"}'}
    expected_query_result = {
                              "status": "success",
                              "data": {
                                "resultType": "vector",
                                "result": [
                                  {
                                    "metric": {
                                      "__name__": "githubactions_workflow_job_success_total",
                                      "instance": "gha_prometheus:80",
                                      "job": "gha_prometheus",
                                      "workflow_job_id": "48831014846",
                                      "workflow_run_id": "30041"
                                    },
                                    "value": [
                                      1753968692.312,
                                      "1"
                                    ]
                                  }
                                ]
                              }
                            }

    prometheus_response = requests.get('http://localhost:9090/api/v1/query',
                                       params=prom_query)
    assert {} == DeepDiff(prometheus_response.json(),
                          expected_query_result,
                          exclude_paths=["root['data']['result'][0]['value'][0]"])

    prom_query = {"query": 'githubactions_workflow_job_failure_total{workflow_run_id="30041"}'}
    expected_query_result = {
                              "status": "success",
                              "data": {
                                "resultType": "vector",
                                "result": [
                                  {
                                    "metric": {
                                      "__name__": "githubactions_workflow_job_failure_total",
                                      "instance": "gha_prometheus:80",
                                      "job": "gha_prometheus",
                                      "workflow_job_id": "48831014846",
                                      "workflow_run_id": "30041"
                                    },
                                    "value": [
                                      1753968692.312,
                                      "1"
                                    ]
                                  }
                                ]
                              }
                            }

    prometheus_response = requests.get('http://localhost:9090/api/v1/query',
                                       params=prom_query)
    assert {} == DeepDiff(prometheus_response.json(),
                          expected_query_result,
                          exclude_paths=["root['data']['result'][0]['value'][0]"])
