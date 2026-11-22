import yaml
import requests
from pathlib import Path

def load_config():
    path = Path(__file__).resolve().parent / "config.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

class ApiClient:
    def __init__(self, role, cfg):
        self.base = cfg["base_url"]+cfg["api_prefix"]
        self.timeout = cfg["timeout"]
        self.auth = None
        self.headers = {}

        if role is None:
            return
        account = cfg["roles"][role]
        token = account.get("token")

        if token:
            self.headers = {"Authorization": "token " + token}
        else:
            self.auth = (account["username"], account["password"])

    def request(self, method, path, **kwargs):
        headers = {**self.headers, **kwargs.pop("headers", {})}
        return requests.request(
            method,
            f"{self.base}{path}",
            timeout=self.timeout,
            auth=self.auth,
            headers=headers,
            **kwargs
        )

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, json=None, **kwargs):
        return self.request("POST", path, json=json, **kwargs)

    def put(self, path, json=None, **kwargs):
        return self.request("PUT", path, json=json, **kwargs)

    def patch(self, path, json=None, **kwargs):
        return self.request("PATCH", path, json=json, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)