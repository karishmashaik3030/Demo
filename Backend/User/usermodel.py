# In-memory user list to get user details
users = []

def get_user_info():
    return users

def create_user(data):
    user_id = len(users) + 1

    user = {
        "id": user_id,
        "name": data["name"],        # type: str
        "email": data["email"],      # type: str
        "age": data.get("age", 0),   # type: int, optional
        "role": data.get("role", "user"),  # type: str, default 'user'
        "is_active": data.get("is_active", True)  # type: bool, default True
    }

    users.append(user)

    return {
        "message": "User created successfully",
        "user": user
    }
