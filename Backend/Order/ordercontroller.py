from flask import Blueprint, request, jsonify
from Order.ordermodel import get_order_info, create_order
from app import app


@app.route("/", methods=["GET"])
def get_order():
    return jsonify(get_order_info())

@app.route("/", methods=["POST"])
def post_order():
    data = request.json
    return jsonify(create_order(data))
