import requests

from config import load_config
from conftest import log_response_hook


class BaseTest:
    cfg = load_config()

    def _login_returns_session(self) -> requests.Session:
        """Perform inline login and return a session with auth headers attached."""
        resp = requests.post(
            f"{self.cfg.base_url}/auth",
            json={
                "username": self.cfg.username,
                "password": self.cfg.password,
                "type": "normal",
            },
            timeout=10,
        )
        resp.raise_for_status()
        token = resp.json()["auth_token"]

        session = requests.Session()
        session.hooks["response"].append(log_response_hook)
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session
