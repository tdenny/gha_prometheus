import os
from datetime import datetime
from flask import abort, Flask, request, jsonify, Response
from prometheus_client import (generate_latest,
                               REGISTRY,
                               GC_COLLECTOR,
                               PLATFORM_COLLECTOR,
                               PROCESS_COLLECTOR)

from gha_prometheus.exceptions import BadRequestMissingField
from gha_prometheus.metrics import (workflow_runs,
                                   workflow_failures,
                                   workflow_successes,
                                   workflow_duration,
                                   job_runs,
                                   job_successes,
                                   job_failures)

# Disable metric collection for garbage collection, platform, and process
REGISTRY.unregister(GC_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(PROCESS_COLLECTOR)

app = Flask(__name__)

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

        if payload['action'] == 'completed':
            workflow_id = payload['workflow']['id']
            duration = calculate_workflow_duration(payload)
            workflow_runs.labels(workflow_id).inc()
            if payload['workflow_run']['conclusion'] == 'success':
                workflow_successes.labels(workflow_id).inc()
            elif payload['workflow_run']['conclusion'] == 'failure':
                workflow_failures.labels(workflow_id).inc()
            workflow_duration.labels(workflow_id).set(duration)
    elif event == "workflow_job":
        validate_workflow_job_payload(payload)

        if payload['action'] == 'completed':
            workflow_job_id = payload['workflow_job']['id']
            workflow_run_id = payload['workflow_job']['run_id']
            job_runs.labels(
                    workflow_run_id=workflow_run_id,
                    workflow_job_id=workflow_job_id
                    ).inc()
            if payload['workflow_job']['conclusion'] == 'success':
                job_successes.labels(
                        workflow_run_id=workflow_run_id,
                        workflow_job_id=workflow_job_id
                        ).inc()
            elif payload['workflow_job']['conclusion'] == 'failure':
                job_failures.labels(
                        workflow_run_id=workflow_run_id,
                        workflow_job_id=workflow_job_id
                        ).inc()

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

def validate_workflow_job_payload(payload):
    """
    Validate that the workflow_job payload contains required fields
    """
    fields = payload.keys()
    missing_fields = []
    if "workflow_job" not in fields:
        missing_fields.append("workflow_job")

    if missing_fields:
        raise BadRequestMissingField(missing_fields)

def calculate_workflow_duration(payload):
    time_format = '%Y-%m-%dT%H:%M:%SZ'
    start_time = datetime.strptime(payload['workflow_run']['run_started_at'], time_format)
    end_time = datetime.strptime(payload['workflow_run']['updated_at'], time_format)
    return (end_time - start_time).seconds

if __name__ == '__main__':
    app.run(debug=True, port=5000)
