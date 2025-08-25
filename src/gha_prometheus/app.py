import os
import json
from datetime import datetime
from flask import abort, Flask, request, jsonify, Response
from prometheus_client import Counter, Gauge, generate_latest
from werkzeug.exceptions import BadRequest, HTTPException
from werkzeug.wrappers.response import Response

app = Flask(__name__)
workflow_runs = Counter('githubactions_workflow_run_total',
                        'Number of workflow executions',
                        ['workflow_id'])
workflow_failures = Counter('githubactions_workflow_run_failure_total',
                            'Number of failed workflow runs',
                            ['workflow_id'])
workflow_successes = Counter('githubactions_workflow_run_success_total',
                             'Number of successful workflow runs',
                             ['workflow_id'])
workflow_duration = Gauge('githubactions_workflow_run_duration_seconds',
                          'Duration of a workflow run in seconds',
                          ['workflow_id'])

class BadRequestMissingField(BadRequest):
    """
    Bad Request with contextual information on missing fields
    """

    def __init__(self, missing_fields=[]):
        rendered_missing_fields = []
        for missing_field in missing_fields:
            rendered_missing_fields.append({
                "field": missing_field,
                "message": f"Field '{missing_field}' is required."
                })

        json_response = json.dumps(
                {
                    "status_code": self.code,
                    "message": "Invalid request payload",
                    "errors": rendered_missing_fields
                }
            )
        response = Response(json_response,
                            self.code,
                            content_type="application/json")
        super().__init__(response=response)

@app.route('/webhook', methods=['POST'])
def receive_webhook():
    """
    Receive the workflow_run webhook event
    """
    event = request.headers.get('X-GitHub-Event')
    if not event:
        return jsonify({"status": "error",
                        "message": "Missing X-GitHub-Event header"}), 400

    payload = request.get_json()
    if event == "workflow_run":
        validate_workflow_run_payload(payload)
        extracted_data = extract_data_from_payload(payload)

        if payload['action'] == 'completed':
            workflow_id = payload['workflow']['id']
            duration = calculate_workflow_duration(payload)
            workflow_runs.labels(workflow_id).inc()
            if payload['workflow_run']['conclusion'] == 'success':
                workflow_successes.labels(workflow_id).inc()
            elif payload['workflow_run']['conclusion'] == 'failure':
                workflow_failures.labels(workflow_id).inc()
            workflow_duration.labels(workflow_id).set(duration)

        return jsonify({"status": "success"}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype='text/plain; version=0.0.4; charset=utf-8')

def validate_workflow_run_payload(payload):
    """
    Validate that the webhook payload contains all required fields
    """
    fields = payload.keys()
    missing_fields = []
    if "workflow" not in fields:
        missing_fields.append("workflow")
    if "workflow_run" not in fields:
        missing_fields.append("workflow_run")

    if missing_fields:
        raise BadRequestMissingField(missing_fields)

def calculate_workflow_duration(payload):
    time_format = '%Y-%m-%dT%H:%M:%SZ'
    start_time = datetime.strptime(payload['workflow_run']['run_started_at'], time_format)
    end_time = datetime.strptime(payload['workflow_run']['updated_at'], time_format)
    return (end_time - start_time).seconds

def extract_data_from_payload(payload):
    workflow = payload.get("workflow")
    workflow_run = payload.get("workflow_run")

    rv = {
        "workflow_id": workflow.get("id"),
        "workflow_run_id": workflow_run.get("id"),
        "conclusion": workflow_run.get("conclusion"),
        "run_started_at": workflow_run.get("run_started_at"),
        "updated_at": workflow_run.get("updated_at")
    }

    return rv

if __name__ == '__main__':
    app.run(debug=True, port=5000)
