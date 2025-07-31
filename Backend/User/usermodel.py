def get_user_info():
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com"
    }

def create_user(data):
    # Business logic goes here – for now just echoing back
    return {
        "message": "User created successfully",
        "user": data
    }
