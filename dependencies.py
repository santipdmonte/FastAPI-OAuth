fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "given_name": "John",
        "family_name": "Doe",
        "email_verified": True,
        "picture": "https://example.com/picture.jpg",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

def get_db():
    return fake_users_db