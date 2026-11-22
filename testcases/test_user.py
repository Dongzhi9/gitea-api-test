import allure
from common import ApiClient

pytestmark = [allure.feature("用户模块")]

def test_get_current_user(admin, cfg):
    resp = admin.get("/user")
    assert resp.status_code == 200
    assert resp.json()["login"] == "dongzhi"

def test_duplicate_username(admin, unique):
    """重名建用户被拒。"""
    name = unique("dup")
    payload = {
        "username":name,
        "email":"name@test.com",
        "password":"password123"
    }

    resp = admin.post("/admin/users", json=payload)
    assert resp.status_code == 201,"第一次建用户应该 201,实际 %s:%s" % (
        resp.status_code, resp.text)

    try:
        resp = admin.post("/admin/users", json=payload)
        assert resp.status_code == 409, "重名建用户应该 409,实际 %s:%s" % (
            resp.status_code, resp.text)
    finally:
        admin.delete("/admin/users/" + name)

def test_no_auth(cfg):
    """不带身份访问 /user,预期401。"""
    anon = ApiClient(None, cfg)
    resp = anon.get("/user")
    assert resp.status_code == 401, "无身份访问应该 401,实际 %s:%s" % (
        resp.status_code, resp.text)

def test_wrong_password(cfg):
    """密码错误,预期401。"""
    client = ApiClient("user_a", cfg)
    username = cfg["roles"]["user_a"]["username"]
    client.auth = (username, "definitely-wrong-password")

    resp = client.get("/user")
    assert resp.status_code == 401, "错误密码应该 401,实际 %s:%s" % (
        resp.status_code, resp.text)


def test_non_admin_cannot_list_users(user_a):
    """普通用户调管理员接口,预期403。"""
    resp = user_a.get("/admin/users?limit=50")
    assert resp.status_code == 403, "普通用户调管理员接口应该 403,实际 %s:%s" % (
        resp.status_code, resp.text)
    
def test_get_user_by_name(admin):
    resp = admin.get("/users/user1")
    assert resp.status_code == 200
    assert resp.json()["login"] == "user1"

def test_get_nonexistent_user(admin, unique):
    name = unique("nobody")
    resp = admin.get("/users/" + name)
    assert resp.status_code == 404

def test_create_user_invalid_email(admin, unique):
    name = unique("badmail")
    resp = admin.post(
        "/admin/users", 
        json={
            "username": name, 
            "email": "not-an-email", 
            "password": "password123"
        })
    assert resp.status_code == 422
    admin.delete("/admin/users/" + name)

def test_create_user_weak_password(admin, unique):
    name = unique("weak")
    resp = admin.post(
        "/admin/users", 
        json={
            "username": name, 
            "email": name + "@test.com", 
            "password": "123"
        })
    assert resp.status_code == 400, "弱密码应该 400,实际 %s:%s" % (
    resp.status_code, resp.text)
    assert resp.json()["message"] == "PasswordIsRequired"

def test_delete_user_then_get(admin, unique):
    name = unique("del")
    resp_p = admin.post(
        "/admin/users", 
        json={
            "username": name, 
            "email": name + "@test.com", 
            "password": "password123"
        })
    assert resp_p.status_code == 201
    resp_d = admin.delete("/admin/users/" + name)
    assert resp_d.status_code == 204
    resp_g = admin.get("/users/" + name)
    assert resp_g.status_code == 404

def test_token_auth(cfg):
    """user_a 走 token 认证,预测能查到自己。"""
    client = ApiClient("user_a", cfg)
    resp = client.get("/user")
    assert resp.status_code == 200, resp.text
    assert resp.json()["login"] == "user1"


def test_create_token_and_list(admin, unique):
    """建 token 后应能在列表里查到。"""
    name = unique("tk")
    resp = admin.post("/users/dongzhi/tokens",
                      json={"name": name, "scopes": ["all"]})
    assert resp.status_code == 201, resp.text

    try:
        resp = admin.get("/users/dongzhi/tokens?limit=50")
        assert resp.status_code == 200, resp.text
        names = [t["name"] for t in resp.json()]
        assert name in names, "刚建的 token 应该在列表里,实际 %s" % names
    finally:
        resp = admin.delete("/users/dongzhi/tokens/" + name)
        assert resp.status_code == 204, resp.text


def test_delete_token(admin, unique):
    """删 token 后列表里应该没有。"""
    name = unique("tk")
    resp = admin.post("/users/dongzhi/tokens",
                      json={"name": name, "scopes": ["all"]})
    assert resp.status_code == 201, resp.text

    resp = admin.delete("/users/dongzhi/tokens/" + name)
    assert resp.status_code == 204, resp.text

    resp = admin.get("/users/dongzhi/tokens?limit=50")
    names = [t["name"] for t in resp.json()]
    assert name not in names, "删掉的 token 不该还在列表里"


def test_invalid_token(cfg):
    """伪造的 token 预测 401。"""
    client = ApiClient("user_a", cfg)
    client.auth = None          # 去掉用户名密码,否则服务端优先用密码认证
    client.headers = {"Authorization": "token fakefakefake1234567890"}
    resp = client.get("/user")
    assert resp.status_code == 401, "假 token 应该 401,实际 %s:%s" % (
    resp.status_code, resp.text)
