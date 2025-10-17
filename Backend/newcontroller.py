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

@app.route("/resources/bulk", methods=["POST"])
def route_bulk_create():
    """Bulk create resources"""
    payload = request.get_json(force=True, silent=True) or []
    if not isinstance(payload, list):
        return jsonify({"error": "expected an array"}), 400
    result = bulk_create_resources(payload)
    return jsonify(result), 201

@app.route("/resources/<int:item_id>", methods=["GET"])
def route_get_resource(item_id):
    """Get single resource"""
    item = get_resource(item_id)
    if not item:
        return jsonify({"error": "not found"}), 404
    return jsonify(item), 200

@app.route("/resources/<int:item_id>", methods=["PUT", "PATCH"])
def route_update_resource(item_id):
    """Update resource"""
    payload = request.get_json(force=True, silent=True) or {}
    try:
        updated = update_resource(item_id, payload)
        return jsonify(updated), 200
    except KeyError:
        return jsonify({"error": "not found"}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/resources/<int:item_id>", methods=["DELETE"])
def route_delete_resource(item_id):
    """Delete resource"""
    deleted = delete_resource(item_id)
    if not deleted:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": True, "item": deleted}), 200

@app.route("/stats/global", methods=["GET"])
def route_global_stats():
    """Compute some global stats across resources"""
    stats = compute_global_stats()
    return jsonify(stats), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
