# Gitea 接口自动化测试框架

[![API Tests](https://github.com/Dongzhi9/gitea-api-test/actions/workflows/test.yml/badge.svg)](https://github.com/Dongzhi9/gitea-api-test/actions/workflows/test.yml)

基于 pytest 对开源项目 Gitea 的 REST API 进行接口自动化测试，覆盖用户、仓库、文件、Issue
四个业务模块及跨用户权限控制，共 49 条用例。

## 技术栈

- Python 3 / requests / PyYAML
- pytest（fixture 管理测试数据与清理）
- allure-pytest（测试报告）
- 被测对象：Gitea（本地实例）

## 目录结构

```
gitea-api-test/
├── common.py              # ApiClient：请求发送、鉴权注入、超时控制
├── conftest.py            # fixture：配置加载、账号、测试数据工厂
├── config.example.yaml    # 配置模板
├── pytest.ini
├── requirements.txt
└── testcases/
    ├── test_user.py         # 用户与令牌
    ├── test_repo.py         # 仓库增删改查
    ├── test_file.py         # 仓库文件内容
    ├── test_issue.py        # Issue 与评论
    └── test_permission.py   # 跨用户权限矩阵
```

## 环境准备

1. 本地启动 Gitea（默认 `http://127.0.0.1:3000`）
2. 创建四个账号：管理员、user1、user2、user3
3. 为 user1、user3 在「设置 → 应用」中生成访问令牌
4. 复制配置模板并填入账号与令牌：

```bash
cp config.example.yaml config.yaml
```

## 运行

```bash
pip install -r requirements.txt

# 全部用例
pytest -q

# 生成 Allure 报告
pytest -q --alluredir=allure-results
allure generate allure-results -o allure-report --clean
allure open allure-report
```

## 用例覆盖

| 模块 | 文件 | 条数 | 覆盖内容 |
|---|---|---|---|
| 用户 | test_user.py | 14 | 当前用户、按名查询、建用户参数校验、重名拒绝、删除确认、令牌生成/列表/删除、密码与令牌鉴权失败 |
| 仓库 | test_repo.py | 7 | 公有/私有仓库创建、详情、修改描述、删除确认、重名拒绝、不存在返回 404 |
| 文件 | test_file.py | 5 | 内容 base64 编码上传、读回校验、带 sha 修改、删除确认、缺 sha 被拒 |
| Issue | test_issue.py | 7 | 创建、查询、修改标题、关闭、评论创建与删除、不存在返回 404 |
| 权限矩阵 | test_permission.py | 16 | 公开/私有仓库的读写边界、非所有者改删被拒、被拒后资源未被破坏、管理员越权改删读、他人提 Issue、未登录的读写限制 |

## 权限矩阵

| 操作 | 仓库所有者 | 其他登录用户 | 未登录 | 管理员 |
|---|---|---|---|---|
| 读公开仓库 | 200 | 200 | 200 | 200 |
| 读私有仓库 | 200 | 404 | 404 | 200 |
| 修改仓库 | 200 | 403 | 401 | 200 |
| 删除仓库 | 204 | 403 | 401 | 204 |
| 提 Issue（公开仓库） | 201 | 201 | 401 | 201 |

## 设计说明

- **鉴权二选一**：`ApiClient` 支持用户名密码（Basic Auth）与访问令牌（`Authorization: token`）
  两种方式，配置了 token 的角色自动走 token，避免在代码或 CI 中明文存放密码。
- **数据自清理**：仓库由 `repo_of` fixture 创建并在会话结束时删除；用例内手工创建的令牌、用户、
  评论通过 `try/finally` 清理，保证重复执行不留残留数据。
- **预期以实测为准**：Gitea 不同接口的返回码并不统一（删仓库 204、删文件 200、改 Issue 201），
  所有预期均通过实际调用确认后写入断言，并为每个断言附带状态码与响应体，失败时可直接定位。

## 持续集成

`.github/workflows/test.yml` 在每次 push 和 PR 时自动执行：

1. 用 Docker 拉起一个 Gitea 实例并等待 `/api/v1/version` 就绪
2. 进入容器创建四个测试账号
3. 生成 CI 专用的 `config.yaml`
4. 安装依赖并执行全部 49 条用例

CI 环境不配置访问令牌，四个角色统一走用户名密码认证，因此本地用令牌、CI 用密码两条路径都被覆盖到。
