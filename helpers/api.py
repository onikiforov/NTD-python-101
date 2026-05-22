import os

import requests

from config import Config


class API:
    def __init__(self, cfg: Config, taiga_session: requests.Session):
        self.cfg = cfg
        self.taiga_session = taiga_session

    def get_user_stories_list(self):
        resp = self.taiga_session.get(
            f"{self.cfg.base_url}/userstories",
            params={"project": self.cfg.project_id},
            timeout=10,
        )

        return resp

    def post_user_story(self, body):
        if self.taiga_session:
            resp = self.taiga_session.post(
                f"{self.cfg.base_url}/userstories",
                json=body,
                timeout=10,
            )
        else:
            resp = requests.post(
                f"{self.cfg.base_url}/userstories",
                json=body,
                timeout=10,
                verify=self.cfg.ssl_verify if os.getenv("HTTPS_PROXY") is not None else None
            )

        return resp

    def get_us_by_id(self, us_id):
        resp = self.taiga_session.get(
            f"{self.cfg.base_url}/userstories/{us_id}",
            timeout=10,
        )

        return resp

    def patch_us_by_id(self, us_id, body):
        resp = self.taiga_session.patch(
            f"{self.cfg.base_url}/userstories/{us_id}",
            json=body,
            timeout=10,
        )

        return resp

    def delete_us_by_id(self, us_id):
        resp = self.taiga_session.delete(
            f"{self.cfg.base_url}/userstories/{us_id}",
            timeout=10,
        )

        return resp

    def post_auth(self, body):
        resp = requests.post(
            f"{self.cfg.base_url}/auth",
            json=body,
            timeout=10,
            verify=self.cfg.ssl_verify if os.getenv("HTTPS_PROXY") is not None else None
        )

        return resp
