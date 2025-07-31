# In-memory user list
users = []

def get_user_info():
    return users

def create_user(data):
    user_id = len(users) + 1
    data["id"] = user_id
    users.append(data)
    return {
        "message": "User created successfully",
        "user": data
    }
