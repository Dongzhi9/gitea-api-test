import allure

pytestmark = [allure.feature("仓库模块")]

def test_create_repo(repo_factory):
    """默认建的是公开仓库。"""
    repo = repo_factory()
    assert repo["private"] is False, "默认建的应该是公开仓库,实际 %s" % repo

def test_create_private_repo(repo_factory):
    """指定 private=True 建的是私有仓库。"""
    repo = repo_factory(private=True)
    assert repo["private"] is True, "指定私有却建成了公开,实际 %s" % repo
 
def test_get_repo(repo_factory, admin):
    """按全名查仓库,预期返回的是新建的。"""
    repo = repo_factory()
    resp = admin.get("/repos/" + repo["full_name"])
    assert resp.status_code == 200, "查仓库预期 200,实际 %s:%s" % (
        resp.status_code, resp.text)
    assert resp.json()["full_name"] == repo["full_name"], "查到的不是新建的"

def test_get_nonexistent_repo(admin, unique):
    """查不存在的仓库,预期404。"""
    resp = admin.get("/repos/dongzhi/" + unique("no"))
    assert resp.status_code == 404, "查不存在仓库应该 404,实际 %s:%s" % (
        resp.status_code, resp.text)


def test_update_repo(repo_factory, admin):
    """只改描述,别的字段不动。"""
    repo = repo_factory()
    resp = admin.patch("/repos/" + repo["full_name"],
                       json={"description": "改过了"})
    assert resp.status_code == 200, "改仓库应该 200,实际 %s:%s" % (
        resp.status_code, resp.text)
    assert resp.json()["description"] == "改过了", "描述没改成新值"


def test_delete_repo(repo_factory, admin):
    """删完再查预期 404。"""
    repo = repo_factory()
    resp = admin.delete("/repos/" + repo["full_name"])
    assert resp.status_code == 204, "删仓库应该 204,实际 %s:%s" % (
        resp.status_code, resp.text)

    resp = admin.get("/repos/" + repo["full_name"])
    assert resp.status_code == 404, "删完再查应该 404,实际 %s:%s" % (
        resp.status_code, resp.text)

def test_duplicate_repo(unique, admin):
    """同名仓库重复创建应被拒,预期409。"""
    name = unique("dup")
    payload = {"name": name, "auto_init": True}

    resp = admin.post("/user/repos", json=payload)
    assert resp.status_code == 201, "第一次建仓库应该 201,实际 %s:%s" % (
        resp.status_code, resp.text)

    try:
        resp = admin.post("/user/repos", json=payload)
        assert resp.status_code == 409, "重名建仓库应该 409,实际 %s:%s" % (
            resp.status_code, resp.text)
    finally:
        admin.delete("/repos/dongzhi/" + name)
