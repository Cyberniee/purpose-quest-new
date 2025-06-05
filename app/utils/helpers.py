import json, urllib.parse

def generate_user_cookies(user: dict, max_age: int = 3600) -> list:
    """
    Generate secure cookies for the user session.
    Includes both secure, HttpOnly tokens and frontend-accessible user data.
    """
    cookies = [
        {
            "key": "access_token",
            "value": user.get("access_token", ""),
            "httponly": True,
            "secure": True,
            "path": "/",
            "samesite": "Lax"
        },
        {
            "key": "refresh_token",
            "value": user.get("refresh_token", ""),
            "httponly": True,
            "secure": True,
            "path": "/",
            "samesite": "Lax"
        },
        {
            "key": "user_id",
            "value": user.get("id", ""),
            "httponly": True,
            "secure": True,
            "path": "/",
            "samesite": "Lax"
        },
        {
            "key": "user_data",
            "value": urllib.parse.quote(json.dumps({
                "user_id": user.get("id"),
                "email": user.get("email"),
                "name": user.get("name", ""),
                "first_login": user.get("first_login", False)
            })),
            "httponly": False,  # Required for frontend access
            "secure": True,
            "path": "/",
            "max_age": max_age,
            "samesite": "Lax"
        }
    ]
    return cookies
