from app import app
from employeemodel import add_employee, get_all_employees
@app.route("/add-employee", methods=["POST"])
def add_employee_route():
    try:
        data = request.get_json()
        employee = add_employee(data)
        return jsonify({"status": "success", "employee": employee}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/get-employee-details", methods=["GET"])
def get_employees_route():
    try:
        employees = get_all_employees()
        return jsonify({"employees": employees}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
                  
