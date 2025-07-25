# models.py

users = []
tasks = []

def create_user(name, email):
    user = {
        "id": len(users) + 1,
        "name": name,
        "email": email
    }
    users.append(user)
    return user

def get_all_users():
    return users

def create_task(title, completed=False):
    task = {
        "id": len(tasks) + 1,
        "title": title,
        "completed": completed
    }
    tasks.append(task)
    return task

def get_all_tasks():
    return tasks
