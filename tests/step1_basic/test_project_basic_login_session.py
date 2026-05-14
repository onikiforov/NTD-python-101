import requests

from config import load_config, Config


class TestProjectBasicLoginSession:
    cfg: Config = load_config()

    def _login(self) -> requests.Session:
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
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session

    def test_get_project_details_return_200(self) -> None:
        # Perform login to create a session
        session = self._login()

        # Send request and get response
        resp = session.get(
            f"{self.cfg.base_url}/projects/{self.cfg.project_id}",
            timeout=10
        )

        # Check status code
        resp.raise_for_status()

        # Additional checks:
        # Get response body and save to a dictionary
        resp_data = resp.json()

        # Assert project id
        assert resp_data["id"] == self.cfg.project_id

        # Assert project name is not empty
        assert resp_data["name"] is not None

        # Assert project slug is not empty
        assert resp_data["slug"] is not None
