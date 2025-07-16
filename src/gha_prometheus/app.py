import os
import json
from flask import abort, Flask, request, jsonify, Response
from prometheus_client import Counter, generate_latest

app = Flask(__name__)
workflow_runs = Counter('githubactions_workflow_run_total',
                        'Number of workflow executions',
                        ['workflow_id'])

@app.route('/webhook', methods=['POST'])
def receive_webhook():
    """
    Receive the workflow_run webhook event
    """
    payload = request.get_json()
    validate_payload(payload)
    extracted_data = extract_data_from_payload(payload)

    workflow_id = extracted_data['workflow_id']

    workflow_runs.labels(workflow_id).inc()

    return jsonify({"status": "success"}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype='text/plain; version=0.0.4; charset=utf-8')

@app.errorhandler(400)
def invalid_request(e):
    return jsonify(message=e.description), 400

def validate_payload(payload):
    """
    Validate that the webhook payload contains all required fields
    """
    fields = payload.keys()
    if "workflow" not in fields or "workflow_run" not in fields:
        abort(400, description="Invalid request payload")

def extract_data_from_payload(payload):
    workflow = payload.get("workflow")
    workflow_run = payload.get("workflow_run")

    rv = {
        "workflow_id": workflow.get("id"),
        "workflow_run_id": workflow_run.get("id"),
        "conclusion": workflow_run.get("conclusion")
    }

    return rv

if __name__ == '__main__':
    app.run(debug=True, port=5000)
