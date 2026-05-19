import requests

from tests.step1_basic.base_test import BaseTest

class TestProjectBasic(BaseTest):
    def _login(self) -> str:
        resp = requests.post(
            f"{self.cfg.base_url}/auth",
            json={
                "username": self.cfg.username,
                "password": self.cfg.password,
                "type": "normal",
            },
            timeout=10,
        )

        assert resp.status_code == 200

        return resp.json()["auth_token"]

    def test_get_project_details_return_200(self) -> None:
        # Perform login to get token
        token = self._login()

        # Set token in headers
        headers = {"Authorization": f"Bearer {token}"}

        # Send request and get response
        resp = requests.get(
            f"{self.cfg.base_url}/projects/{self.cfg.project_id}",
            headers=headers,
            timeout=10
        )

        # Assert response status code
        assert resp.status_code == 200

        # Additional checks:
        # Get response body and save to a dictionary
        resp_data = resp.json()

        # Assert project id
        assert resp_data["id"] == self.cfg.project_id

        # Assert project name is not empty
        assert resp_data["name"] is not None

        # Assert project slug is not empty
        assert resp_data["slug"] is not None
