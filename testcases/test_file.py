import base64
import allure

pytestmark = [allure.feature("文件模块")]

def test_create_file(repo_factory, admin):
    """在仓库里建文件,预期201。"""
    repo = repo_factory()
    branch = repo["default_branch"]

    content = base64.b64encode("第一版内容".encode()).decode()
    path = "/repos/%s/contents/readme.md" % repo["full_name"]

    resp = admin.post(path, json={
        "content": content,
        "message": "建文件",
        "branch": branch
    })
    assert resp.status_code == 201,"建文件应该 201,实际 %s:%s" % (
        resp.status_code, resp.text)
    assert "sha" in resp.json()["content"]

def test_get_file_content(repo_factory, admin):
    """读回文件内容,应该和写进去的一致。"""
    repo = repo_factory()
    branch = repo["default_branch"]
    content = base64.b64encode("第一版内容".encode()).decode()
    path = "/repos/%s/contents/readme.md" % repo["full_name"]

    resp = admin.post(path, json={
        "content": content,
        "message": "建文件",
        "branch": branch
    })
    assert resp.status_code == 201, resp.text

    resp = admin.get(path)
    assert resp.status_code == 200, "读文件应该 200,实际 %s:%s" % (
        resp.status_code, resp.text)

    text = base64.b64decode(resp.json()["content"]).decode()
    assert text == "第一版内容", "读回来的内容不对,实际 %s" % text

def test_update_file(repo_factory, admin):
    """改文件后再读,应该是新内容。"""
    repo = repo_factory()
    branch = repo["default_branch"]
    path = "/repos/%s/contents/readme.md" % repo["full_name"]

    content = base64.b64encode("第一版内容".encode()).decode()
    resp = admin.post(path, json={
        "content": content, "message": "建文件", "branch": branch
    })
    assert resp.status_code == 201, resp.text
    sha = resp.json()["content"]["sha"]

    new_content = base64.b64encode("第二版内容".encode()).decode()
    resp = admin.put(path, json={
        "content": new_content, "message": "改文件", "sha": sha, "branch": branch
    })
    assert resp.status_code == 200, "改文件应该 200,实际 %s:%s" % (
        resp.status_code, resp.text)

    resp = admin.get(path)
    text = base64.b64decode(resp.json()["content"]).decode()
    assert text == "第二版内容", "读回来还是老内容,实际 %s" % text


def test_delete_file(repo_factory, admin):
    """删文件后再读,应该 404。"""
    repo = repo_factory()
    branch = repo["default_branch"]
    path = "/repos/%s/contents/readme.md" % repo["full_name"]

    content = base64.b64encode("第一版内容".encode()).decode()
    resp = admin.post(path, json={
        "content": content, "message": "建文件", "branch": branch
    })
    assert resp.status_code == 201, resp.text
    sha = resp.json()["content"]["sha"]

    resp = admin.delete(path, json={
        "message": "删文件", "sha": sha, "branch": branch
    })
    assert resp.status_code == 200, "删文件应该 200,实际 %s:%s" % (
        resp.status_code, resp.text)

    resp = admin.get(path)
    assert resp.status_code == 404, "删完再读应该 404,实际 %s:%s" % (
        resp.status_code, resp.text)


def test_update_file_without_sha(repo_factory, admin):
    """不带 sha 直接改文件,应该被拒。"""
    repo = repo_factory()
    branch = repo["default_branch"]
    path = "/repos/%s/contents/readme.md" % repo["full_name"]

    content = base64.b64encode("第一版内容".encode()).decode()
    resp = admin.post(path, json={
        "content": content, "message": "建文件", "branch": branch
    })
    assert resp.status_code == 201, resp.text

    new_content = base64.b64encode("第二版内容".encode()).decode()
    resp = admin.put(path, json={
        "content": new_content, "message": "改文件", "branch": branch
    })
    assert resp.status_code == 422, "不带 sha 改文件应该 422,实际 %s:%s" % (
    resp.status_code, resp.text)
    assert resp.json()["message"].startswith("repository file already exists")
