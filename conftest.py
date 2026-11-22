import time
import pytest
from common import load_config, ApiClient


@pytest.fixture(scope="session")
def cfg():
    return load_config()             

@pytest.fixture(scope="session")
def admin(cfg):
    return ApiClient("admin", cfg)    

@pytest.fixture(scope="session")
def user_a(cfg):
    return ApiClient("user_a", cfg)     

@pytest.fixture(scope="session")
def user_b(cfg):
    return ApiClient("user_b", cfg)

@pytest.fixture(scope="session")
def unique():
    def _make(name="t"):
        return f"{name}_{int(time.time()*1000)}"

    return _make

@pytest.fixture(scope="session") 
def repo_factory(admin, unique):
    created = []

    def _create(private=False):
        name = unique("repo")
        resp = admin.post("/user/repos",json={
            "name":name,
            "private":private,
            "auto_init":True
        })
        assert resp.status_code == 201,resp.text
        data = resp.json()
        created.append(data["full_name"])
        return data

    yield _create

    for full_name in created:
        admin.delete("/repos/" + full_name)

@pytest.fixture(scope="session")
def repo_of(unique):
    created = []

    def _create(client, private=False):
        name = unique("perm")
        resp = client.post("/user/repos",json={
            "name":name, "private":private, "auto_init":True
        })
        assert resp.status_code == 201, resp.text
        data = resp.json()
        created.append((client, data["full_name"]))
        return data

    yield _create

    for client, full_name in created:
        client.delete("/repos/" + full_name)