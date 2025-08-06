from flask import Blueprint, request, jsonify
from User.usermodel import get_user_info, create_user
from app import app

@app.route("/get-users", methods=["GET"])
def get_user():
    result = get_user_info()
    return jsonify(result)

@app.route("/create-users", methods=["POST"])
def post_user():
    data = request.json
    result = create_user(data)
    return jsonify(result)
