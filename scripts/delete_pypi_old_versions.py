#!/usr/bin/env python3
"""
删除 PyPI 上的旧版本，这些版本包含隐私信息。

用法:
    python3 scripts/delete_pypi_old_versions.py
    然后输入 PyPI 用户名和密码。
"""

import sys
import requests

PROJECT = "cybernetics-agent"
VERSIONS_TO_DELETE = ["0.6.0", "0.6.1", "0.6.2", "0.6.3"]


def delete_version(username: str, password: str, version: str) -> bool:
    """通过 PyPI API 删除指定版本。"""
    session = requests.Session()

    # 1. 获取登录页面的 CSRF token
    login_url = "https://pypi.org/account/login/"
    resp = session.get(login_url)
    if resp.status_code != 200:
        print(f"  ❌ 无法访问登录页面: {resp.status_code}")
        return False

    # 提取 CSRF token
    csrf_token = None
    for line in resp.text.split("\n"):
        if 'name="csrf_token"' in line and 'value="' in line:
            start = line.find('value="') + 7
            end = line.find('"', start)
            csrf_token = line[start:end]
            break

    if not csrf_token:
        print("  ❌ 无法提取 CSRF token")
        return False

    # 2. 登录
    login_data = {
        "csrf_token": csrf_token,
        "username": username,
        "password": password,
    }
    resp = session.post(login_url, data=login_data, allow_redirects=True)
    if resp.status_code != 200 or "account/login" in resp.url:
        print("  ❌ 登录失败，请检查用户名密码")
        return False

    print(f"  ✅ 登录成功")

    # 3. 获取版本管理页面的 CSRF token
    manage_url = f"https://pypi.org/manage/project/{PROJECT}/release/{version}/"
    resp = session.get(manage_url)
    if resp.status_code != 200:
        print(f"  ❌ 无法访问版本管理页面: {resp.status_code}")
        return False

    csrf_token = None
    for line in resp.text.split("\n"):
        if 'name="csrf_token"' in line and 'value="' in line:
            start = line.find('value="') + 7
            end = line.find('"', start)
            csrf_token = line[start:end]
            break

    if not csrf_token:
        print("  ❌ 无法提取版本管理页面的 CSRF token")
        return False

    # 4. 发送删除请求
    delete_url = f"https://pypi.org/manage/project/{PROJECT}/release/{version}/destroy/"
    delete_data = {
        "csrf_token": csrf_token,
        "confirm_version": version,
    }
    resp = session.post(delete_url, data=delete_data, allow_redirects=True)

    if resp.status_code == 200 and "has been deleted" in resp.text:
        print(f"  ✅ 版本 {version} 已删除")
        return True
    elif resp.status_code == 200 and "yanked" in resp.text.lower():
        print(f"  ✅ 版本 {version} 已标记为 yanked")
        return True
    else:
        print(f"  ❌ 删除失败: {resp.status_code}")
        return False


def main():
    print("=" * 60)
    print(f"即将删除 PyPI 项目 {PROJECT} 的以下版本:")
    for v in VERSIONS_TO_DELETE:
        print(f"  - {v}")
    print("=" * 60)

    username = input("PyPI 用户名: ").strip()
    password = input("PyPI 密码: ").strip()

    print()
    success_count = 0
    for version in VERSIONS_TO_DELETE:
        print(f"删除 {version}...")
        if delete_version(username, password, version):
            success_count += 1
        print()

    print(f"结果: 成功删除 {success_count}/{len(VERSIONS_TO_DELETE)} 个版本")

    if success_count < len(VERSIONS_TO_DELETE):
        print("\n提示: 如果脚本删除失败，可以手动登录 https://pypi.org/manage/project/cybernetics-agent/releases/")
        print("      点击每个版本号旁边的 "Delete" 按钮删除。")


if __name__ == "__main__":
    main()
