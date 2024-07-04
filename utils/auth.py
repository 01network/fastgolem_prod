# Mock user database
users = {
    "user1": {"password": "pass1"},
    "user2": {"password": "pass2"}
}


# Auth function
def authenticate(username, password):
    if username is users and users[username]["password"] == password:
        return True
    return False