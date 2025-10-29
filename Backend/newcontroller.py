from flask import Flask, request, jsonify, abort
from model import (
    ping,
    list_all_resources,
    create_resource,
    get_resource,
    update_resource,
    delete_resource,
    bulk_create_resources,
    compute_global_stats,
)

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def route_ping():
    """Health check"""
    return jsonify({"status": "ok", "message": ping()}), 200

@app.route("/resources", methods=["GET"])
def route_list_resources():
    """List all resources"""
    resources = list_all_resources()
    return jsonify(resources), 200

@app.route("/resources", methods=["POST"])
def route_create_resource():
    """Create a resource"""
    payload = request.get_json(force=True, silent=True) or {}
    try:
        item = create_resource(payload)
        return jsonify(item), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
