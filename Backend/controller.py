from flask import Blueprint, request, jsonify
from api_testing import create_user, get_all_users, create_task, get_all_tasks
from app import app

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(get_all_users()), 200

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(get_all_tasks()), 200

@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    if not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email are required'}), 400
    user = create_user(data['name'], data['email'])
    return jsonify(user), 201

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.json
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    task = create_task(data['title'], data.get('completed', False))
    return jsonify(task), 201
