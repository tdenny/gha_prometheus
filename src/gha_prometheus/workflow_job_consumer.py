from gha_prometheus.exceptions import BadRequestMissingField
from gha_prometheus.metrics import (job_runs,
                                    job_successes,
                                    job_failures)

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


