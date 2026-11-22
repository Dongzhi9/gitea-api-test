import allure
from common import ApiClient

pytestmark = [allure.feature("权限矩阵")]

def test_create_repo_owned_by_user(repo_of, user_a):
    """用user1的身份建仓库,归属应为user1"""
    repo = repo_of(user_a)
    assert repo["owner"]["login"] == "user1", "归属错误,实际%s" % repo["owner"]["login"]

def test_other_user_can_read_public_repo(repo_of, user_a, user_b):
    """user2能访问别人的公开仓库"""
    repo = repo_of(user_a)
    resp = user_b.get("/repos/" + repo["full_name"])
    assert resp.status_code == 200, "读取公开仓库应为200,实际 %s:%s" % (
        resp.status_code, resp.text)

def test_other_user_cannot_read_private_repo(repo_of, user_a, user_b):
    """别人的私有仓库,user2读不到。"""
    repo = repo_of(user_a, private=True)
    resp = user_b.get("/repos/" + repo["full_name"])
    assert resp.status_code == 404, "读取私有仓库应为404,实际 %s:%s" % (
        resp.status_code, resp.text)

def test_anonymous_can_read_public_repo(repo_of, user_a, cfg):
    """不登录也能读公开仓库。"""
    repo = repo_of(user_a)
    anon = ApiClient(None, cfg)
    resp = anon.get("/repos/" + repo["full_name"])
    assert resp.status_code == 200, "匿名读公开仓库应该 200,实际 %s:%s" % (
        resp.status_code, resp.text)

def test_anonymous_cannot_read_private_repo(repo_of, user_a, cfg):
    """不登录读不到私有仓库。"""
    repo = repo_of(user_a, private=True)
    anon = ApiClient(None, cfg)
    resp = anon.get("/repos/" + repo["full_name"])
    assert resp.status_code == 404, "匿名读私有仓库应该 404,实际 %s:%s" % (
        resp.status_code, resp.text)

def test_owner_can_update_own_repo(repo_of, user_a):
    """仓库主人改自己的仓库,应该成功。"""
    repo = repo_of(user_a)
    resp = user_a.patch("/repos/" + repo["full_name"],
                        json={"description": "我自己改"})
    assert resp.status_code == 200, "改自己仓库应该 200,实际 %s:%s" % (
        resp.status_code, resp.text)
    assert resp.json()["description"] == "我自己改", "描述没改成新值"

def test_other_user_cannot_update_repo(repo_of, user_a, user_b):
    """非主人改别人的仓库,应该被拒。"""
    repo = repo_of(user_a)
    resp = user_b.patch("/repos/" + repo["full_name"],
                        json={"description": "别人来改"})
    assert resp.status_code == 403, "改别人仓库应该 403,实际 %s:%s" % (
        resp.status_code, resp.text)
    assert resp.json()["message"].startswith(
        "user should be an owner or a collaborator")

def test_other_user_cannot_delete_repo(repo_of, user_a, user_b):
    """非主人删别人的仓库,应该被拒。"""
    repo = repo_of(user_a)
    resp = user_b.delete("/repos/" + repo["full_name"])
    assert resp.status_code == 403, "删别人仓库应该 403,实际 %s:%s" % (
        resp.status_code, resp.text)
    assert resp.json()["message"] == "user has no permission to manage the danger zone"

def test_repo_survives_failed_delete(repo_of, user_a, user_b):
    """删别人的仓库被拒之后,仓库应该还在。"""
    repo = repo_of(user_a)
    user_b.delete("/repos/" + repo["full_name"])

    resp = user_a.get("/repos/" + repo["full_name"])
    assert resp.status_code == 200, "被拒之后仓库不该消失,实际 %s:%s" % (
        resp.status_code, resp.text)

def test_admin_can_update_others_repo(repo_of, user_a, admin):
    """管理员能改别人的仓库。"""
    repo = repo_of(user_a)
    resp = admin.patch("/repos/" + repo["full_name"],
                       json={"description": "管理员改的"})
    assert resp.status_code == 200, "管理员改仓库应该 200,实际 %s:%s" % (
        resp.status_code, resp.text)
    assert resp.json()["description"] == "管理员改的", "描述没改成新值"

def test_admin_can_delete_others_repo(repo_of, user_a, admin):
    """管理员能删别人的仓库,删完就查不到了。"""
    repo = repo_of(user_a)
    resp = admin.delete("/repos/" + repo["full_name"])
    assert resp.status_code == 204, "管理员删仓库应该 204,实际 %s:%s" % (
        resp.status_code, resp.text)

    resp = user_a.get("/repos/" + repo["full_name"])
    assert resp.status_code == 404, "删完应该 404,实际 %s:%s" % (
        resp.status_code, resp.text)

def test_other_user_can_open_issue(repo_of, user_a, user_b):
    """别人能不能在公开仓库上提 Issue。"""
    repo = repo_of(user_a)
    resp = user_b.post("/repos/%s/issues" % repo["full_name"],
                       json={"title": "路人提的"})
    assert resp.status_code == 201, "公开仓库应该允许别人提 Issue,实际 %s:%s" % (
        resp.status_code, resp.text)
    assert resp.json()["user"]["login"] == "user2", "提 Issue 的人不对,实际 %s" % (
        resp.json()["user"]["login"])
    assert resp.json()["repository"]["owner"] == "user1", "Issue 挂错仓库了"

def test_anonymous_cannot_update_repo(repo_of, user_a, cfg):
    """未登录不能改仓库。"""
    repo = repo_of(user_a)
    anon = ApiClient(None, cfg)
    resp = anon.patch("/repos/" + repo["full_name"],
                      json={"description": "匿名改"})
    assert resp.status_code == 401, "未登录改仓库应该 401,实际 %s:%s" % (
        resp.status_code, resp.text)


def test_anonymous_cannot_delete_repo(repo_of, user_a, cfg):
    """未登录不能删仓库。"""
    repo = repo_of(user_a)
    anon = ApiClient(None, cfg)
    resp = anon.delete("/repos/" + repo["full_name"])
    assert resp.status_code == 401, "未登录删仓库应该 401,实际 %s:%s" % (
        resp.status_code, resp.text)


def test_anonymous_cannot_open_issue(repo_of, user_a, cfg):
    """未登录不能提 Issue。"""
    repo = repo_of(user_a)
    anon = ApiClient(None, cfg)
    resp = anon.post("/repos/%s/issues" % repo["full_name"],
                     json={"title": "匿名提的"})
    assert resp.status_code == 401, "未登录提 Issue 应该 401,实际 %s:%s" % (
        resp.status_code, resp.text)


def test_admin_can_read_private_repo(repo_of, user_a, admin):
    """管理员能读别人的私有仓库。"""
    repo = repo_of(user_a, private=True)
    resp = admin.get("/repos/" + repo["full_name"])
    assert resp.status_code == 200, "管理员读私有仓库应该 200,实际 %s:%s" % (
        resp.status_code, resp.text)
