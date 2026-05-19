import allure

from tests.step1_basic.base_test import BaseTest


class TestProjectBasicLoginSessionWithAllure(BaseTest):
    @allure.feature("Project")
    @allure.story("Basic")
    def test_get_project_details_return_200(self) -> None:
        with allure.step("Login"):
            # Perform login to create a session
            session = self._login_returns_session()

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
