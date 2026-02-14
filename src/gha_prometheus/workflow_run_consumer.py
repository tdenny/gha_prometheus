from datetime import datetime
from gha_prometheus.metrics import (workflow_runs,
                                    workflow_failures,
                                    workflow_successes,
                                    workflow_duration)
from gha_prometheus.exceptions import BadRequestMissingField

def consume_workflow_run_event(payload):
    validate_workflow_run_payload(payload)

    if payload['action'] == 'completed':
        workflow_id = payload['workflow']['id']
        duration = calculate_workflow_duration(payload)
        increment_workflow_run(workflow_id)
        if payload['workflow_run']['conclusion'] == 'success':
            increment_workflow_success(workflow_id)
        elif payload['workflow_run']['conclusion'] == 'failure':
            increment_workflow_failure(workflow_id)
        workflow_duration.labels(workflow_id).set(duration)

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

def increment_workflow_run(workflow_id):
    workflow_runs.labels(workflow_id).inc()

def increment_workflow_success(workflow_id):
    workflow_successes.labels(workflow_id).inc()

def increment_workflow_failure(workflow_id):
    workflow_failures.labels(workflow_id).inc()

def calculate_workflow_duration(payload):
    time_format = '%Y-%m-%dT%H:%M:%SZ'
    start_time = datetime.strptime(payload['workflow_run']['run_started_at'], time_format)
    end_time = datetime.strptime(payload['workflow_run']['updated_at'], time_format)
    return (end_time - start_time).seconds

