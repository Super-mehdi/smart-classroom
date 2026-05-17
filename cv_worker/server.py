import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from celery_app import celery_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Allow requests from http://localhost:3000 (standard React dev port)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.route("/start", methods=["POST"])
def start_pipeline():
    try:
        logger.info("Sending start_cv_pipeline task")
        celery_app.send_task("tasks.start_cv_pipeline")
        return jsonify({"status": "started"}), 200

    except Exception as e:
        logger.error(f"Failed to send start task: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/stop", methods=["POST"])
def stop_pipeline():
    try:
        logger.info("Sending stop_cv_pipeline task")
        celery_app.send_task("tasks.stop_cv_pipeline")
        return jsonify({"status": "stopped"}), 200

    except Exception as e:
        logger.error(f"Failed to send stop task: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
