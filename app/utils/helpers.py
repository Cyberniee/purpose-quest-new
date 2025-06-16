import json, urllib.parse, logging

logger = logging.getLogger(__name__)


def generate_user_cookies(user: dict, max_age: int = 3600) -> list:
    """
    Generate secure cookies for the user session.
    Includes both secure, HttpOnly tokens and frontend-accessible user data.
    """
    print(f"User in cookie gen: {user}")
    cookies = [
        {
            "key": "access_token",
            "value": user.get("access_token", ""),
            "httponly": True,
            "secure": True,
            "path": "/",
            "samesite": "Lax",
        },
        {
            "key": "refresh_token",
            "value": user.get("refresh_token", ""),
            "httponly": True,
            "secure": True,
            "path": "/",
            "samesite": "Lax",
        },
        {
            "key": "email",
            "value": user.get("email", ""),
            "httponly": True,
            "secure": True,
            "path": "/",
            "samesite": "Lax",
        },
        {
            "key": "sub",
            "value": user.get("sub", ""),
            "httponly": True,
            "secure": True,
            "path": "/",
            "samesite": "Lax",
        },
        {
            "key": "id",
            "value": user.get("id", ""),
            "httponly": True,
            "secure": True,
            "path": "/",
            "samesite": "Lax",
        },
        {
            "key": "user_data",
            "value": urllib.parse.quote(
                json.dumps(
                    {
                        "sub": user.get("sub"),
                        "email": user.get("email"),
                        "name": user.get("first_name", ""),
                        "id": user.get('id', ''),
                        "first_login": user.get("first_login", False),
                    }
                )
            ),
            "httponly": False,  # Required for frontend access
            "secure": True,
            "path": "/",
            "max_age": max_age,
            "samesite": "Lax",
        },
    ]
    return cookies


def parse_user_data_cookie(cookie_value: str) -> dict | None:
    try:
        decoded = urllib.parse.unquote(cookie_value)
        return json.loads(decoded)
    except Exception as e:
        logger.warning(f"Failed to decode user_data cookie: {e}")
        return None