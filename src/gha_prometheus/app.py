import os
import json
from flask import Flask, request, jsonify, Response
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
    extracted_data = extract_data_from_payload(payload)

    workflow_id = extracted_data['workflow_id']

    workflow_runs.labels(workflow_id).inc()

    return jsonify({"status": "success"}), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype='text/plain; version=0.0.4; charset=utf-8')

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
