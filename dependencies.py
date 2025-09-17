fake_users_db = {
    "johndoe@example.com": {
        "username": "johndoe@example.com",
        "given_name": "John",
        "family_name": "Doe",
        "email_verified": True,
        "picture": "https://example.com/picture.jpg",
        "full_name": "John Doe",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "pedemax123@gmail.com": {
        "username": "pedemax123@gmail.com",
        "given_name": "Santiago",
        "family_name": None,
        "email_verified": True,
        "picture": None,
        "full_name": None,
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

def get_db():
    return fake_users_db