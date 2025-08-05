# employee_model.py

# Simple in-memory storage for demo purposes
employees = []

def add_employee(data):
    employees.append(data)
    return data

def get_all_employees():
    return employees
