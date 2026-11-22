import allure

pytestmark = [allure.feature("Issue模块")]

def test_create_issue(repo_factory, admin):
    """建 Issue,预期201。"""
    repo = repo_factory()
    path = "/repos/%s/issues" % repo["full_name"]

    resp = admin.post(path, json={"title": "登录打不开", "body": "点了没反应"})
    assert resp.status_code == 201, "建 Issue 应该 201,实际 %s:%s" % (
        resp.status_code, resp.text)
    assert resp.json()["title"] == "登录打不开", "标题不对,实际 %s" % resp.json()["title"]

def test_get_issue(repo_factory, admin):
    """按编号查 Issue,预期200。"""
    repo = repo_factory()
    path = "/repos/%s/issues" % repo["full_name"]

    resp = admin.post(path, json={"title": "登录打不开", "body": "点了没反应"})
    assert resp.status_code == 201, resp.text
    number = resp.json()["number"]

    resp = admin.get(path + "/" + str(number))
    assert resp.status_code == 200, "查 Issue 应该 200,实际 %s:%s" % (
        resp.status_code, resp.text)
    assert resp.json()["number"] == number, "查到的不是刚建的那条"

def test_update_issue_title(repo_factory, admin):
    """改标题后,重新查应该是新标题。"""
    repo = repo_factory()
    path = "/repos/%s/issues" % repo["full_name"]

    resp = admin.post(path, json={"title": "登录打不开", "body": "点了没反应"})
    assert resp.status_code == 201, resp.text
    number = resp.json()["number"]

    resp = admin.patch(path + "/" + str(number),
                       json={"title": "登录打不开(已确认)"})
    assert resp.status_code == 201, "改 Issue 应该 201,实际 %s:%s" % (
        resp.status_code, resp.text)

    resp = admin.get(path + "/" + str(number))
    assert resp.json()["title"] == "登录打不开(已确认)", "标题没改成新值,实际 %s" % (
        resp.json()["title"])

def test_close_issue(repo_factory, admin):
    """关闭 Issue,状态应变成 closed。"""
    repo = repo_factory()
    path = "/repos/%s/issues" % repo["full_name"]

    resp = admin.post(path, json={"title": "登录打不开", "body": "点了没反应"})
    assert resp.status_code == 201, resp.text
    number = resp.json()["number"]

    resp = admin.patch(path + "/" + str(number), json={"state": "closed"})
    assert resp.status_code == 201, "关闭 Issue 应该 201,实际 %s:%s" % (
        resp.status_code, resp.text)
    assert resp.json()["state"] == "closed", "状态没关掉,实际 %s" % (
        resp.json()["state"])

def test_create_comment(repo_factory, admin):
    """建评论后,评论列表里内容预期存在。"""
    repo = repo_factory()
    path = "/repos/%s/issues" % repo["full_name"]

    resp = admin.post(path, json={"title": "登录打不开", "body": "点了没反应"})
    assert resp.status_code == 201, resp.text
    number = resp.json()["number"]

    resp = admin.post(path + "/" + str(number) + "/comments",
                      json={"body": "我也遇到了"})
    assert resp.status_code == 201, "建评论应该 201,实际 %s:%s" % (
        resp.status_code, resp.text)

    resp = admin.get(path + "/" + str(number) + "/comments")
    assert resp.status_code == 200, "查评论列表应该 200,实际 %s:%s" % (
        resp.status_code, resp.text)
    comments = resp.json()
    assert len(comments) == 1, "评论应该有 1 条,实际 %d 条" % len(comments)
    assert comments[0]["body"] == "我也遇到了", "评论内容不对,实际 %s" % (
        comments[0]["body"])

def test_delete_comment(repo_factory, admin):
    """删评论后,列表里内容消失。"""
    repo = repo_factory()
    path = "/repos/%s/issues" % repo["full_name"]

    resp = admin.post(path, json={"title": "登录打不开", "body": "点了没反应"})
    assert resp.status_code == 201, resp.text
    number = resp.json()["number"]

    resp = admin.post(path + "/" + str(number) + "/comments",
                      json={"body": "我也遇到了"})
    assert resp.status_code == 201, resp.text
    comment_id = resp.json()["id"]

    resp = admin.delete(path + "/" + str(number) + "/comments/" + str(comment_id))
    assert resp.status_code == 204, "删评论预期 204,实际 %s:%s" % (
        resp.status_code, resp.text)

    resp = admin.get(path + "/" + str(number) + "/comments")
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) == 0, "删完评论列表预期为空,实际 %d 条" % len(resp.json())

def test_get_nonexistent_issue(repo_factory, admin):
    """查不存在的 Issue,预期404。"""
    repo = repo_factory()
    resp = admin.get("/repos/%s/issues/999999" % repo["full_name"])
    assert resp.status_code == 404, "查不存在 Issue 预期 404,实际 %s:%s" % (
        resp.status_code, resp.text)
