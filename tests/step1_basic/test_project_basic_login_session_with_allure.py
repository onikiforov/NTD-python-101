import allure
import requests

from config import load_config, Config


class TestProjectBasicLoginSessionWithAllure:
    cfg: Config = load_config() # TODO: this should be moved to fixtures

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

    @allure.feature("Project")
    @allure.story("Basic")
    def test_get_project_details_return_200(self) -> None:
        with allure.step("Login"):
            # Perform login to create a session
            session = self._login()

        with allure.step("Get project details"):
            # Send request and get response
            resp = session.get(
                f"{self.cfg.base_url}/projects/{self.cfg.project_id}",
                timeout=10
            )

            # Check status code
            resp.raise_for_status()

        with allure.step("Assert response details"):
            # Additional checks:
            # Get response body and save to a dictionary
            resp_data = resp.json()

            # Assert project id
            assert resp_data["id"] == self.cfg.project_id

            # Assert project name is not empty
            assert resp_data["name"] is not None

            # Assert project slug is not empty
            assert resp_data["slug"] is not None
