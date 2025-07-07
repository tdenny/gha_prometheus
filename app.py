import json
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

DATA_FILE = 'webhook_data.json'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

@app.route('/webhook', methods=['POST'])
def receive_webhook():
    """
    Receive the workflow_run webhook event
    """
    if request.is_json:
        payload = request.get_json()

        workflow = payload.get("workflow")
        workflow_run = payload.get("workflow_run")

        extracted_data = {
            "workflow_id": workflow.get("id"),
            "workflow_run_id": workflow_run.get("id"),
            "conclusion": workflow_run.get("conclusion")
        }

        try:
            with open(DATA_FILE, 'r+') as f:
                existing_data = json.load(f)
                existing_data.append(extracted_data)
                f.seek(0)
                json.dump(existing_data, f, indent=4)
                f.truncate()
            print(f"Stored data: {extracted_data}")
            return jsonify({"status": "success"}), 200
        except Exception as e:
            printf("Error storing data: {e}")
            return jsonify({"status": "error", "message": "Failed to store data"}), 500
    else:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
