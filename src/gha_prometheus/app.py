import os
from flask import abort, Flask, request, jsonify, Response
from prometheus_client import (generate_latest,
                               REGISTRY,
                               GC_COLLECTOR,
                               PLATFORM_COLLECTOR,
                               PROCESS_COLLECTOR)

from gha_prometheus.workflow_job_consumer import consume_workflow_job_event
from gha_prometheus.workflow_run_consumer import consume_workflow_run_event

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

@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype='text/plain; version=0.0.4; charset=utf-8')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
