import os
from flask import abort, Flask, request, jsonify, Response
from prometheus_client import (generate_latest,
                               REGISTRY,
                               GC_COLLECTOR,
                               PLATFORM_COLLECTOR,
                               PROCESS_COLLECTOR)

from gha_prometheus.workflow_run_consumer import consume_workflow_run_event
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
        consume_workflow_run_event(payload)
    elif event == "workflow_job":
        consume_workflow_job_event(payload)

    return jsonify({"status": "success"}), 200


def consume_workflow_job_event(payload):
    validate_workflow_job_payload(payload)

    if payload['action'] == 'completed':
        workflow_job_id = payload['workflow_job']['id']
        workflow_run_id = payload['workflow_job']['run_id']
        increment_job_run(workflow_run_id, workflow_job_id)
        if payload['workflow_job']['conclusion'] == 'success':
            increment_job_success(workflow_run_id, workflow_job_id)
        elif payload['workflow_job']['conclusion'] == 'failure':
            increment_job_failure(workflow_run_id, workflow_job_id)


def increment_job_run(run_id, job_id):
    job_runs.labels(
        workflow_run_id=run_id,
        workflow_job_id=job_id
    ).inc()

def increment_job_success(run_id, job_id):
    job_successes.labels(
        workflow_run_id=run_id,
        workflow_job_id=job_id
    ).inc()

def increment_job_failure(run_id, job_id):
    job_failures.labels(
        workflow_run_id=run_id,
        workflow_job_id=job_id
    ).inc()


@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype='text/plain; version=0.0.4; charset=utf-8')


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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
