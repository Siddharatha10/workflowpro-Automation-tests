import requests

from config import API_BASE_URL


def login(email: str, password: str) -> str:
    """Returns a bearer token for the given credentials."""
    resp = requests.post(
        f"{API_BASE_URL}/api/v1/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["token"]
