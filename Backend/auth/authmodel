# model.py

USERS = {
    "john": {
        "password": "secret123",
        "email": "john.doe@example.com"
    }
}

def authenticate_user(username, password):
    """
    Validates username and password.
    Returns user dict if valid, else None.
    """
    user = USERS.get(username)
    if user and user["password"] == password:
        return user
    return None

def get_all_public_data():
    """
    Example: public resource.
    """
    return [
        {"id": 1, "title": "Public Article 1"},
        {"id": 2, "title": "Public Article 2"},
    ]

def get_all_private_data():
    """
    Example: protected resource.
    """
    return [
        {"id": 101, "secret": "Classified Data A"},
        {"id": 102, "secret": "Classified Data B"},
    ]
