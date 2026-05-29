import os
import requests
import base64
import json
import time
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

API_BASE = "https://api.github.com/repos/esterTion/yumesute_master_db_diff/contents"
LOCAL_DATA_DIR = "data"
FILES_TO_UPDATE = [
    "CharacterMaster.json",
    "EffectMaster.json",
    "PosterAbilityMaster.json",
]
VERSION_FILE = "!version.txt"
NO_PROXY = {"http": None, "https": None}
MAX_RETRIES = 3
RETRY_DELAY = 1


def download_file_via_blob(git_url):  # download via Git Blob API
    resp = requests.get(git_url, timeout=30, verify=False, proxies=NO_PROXY)
    resp.raise_for_status()
    blob_data = resp.json()
    if blob_data.get("encoding") != "base64":
        raise ValueError("Blob 编码不是 base64")
    return base64.b64decode(blob_data["content"])


def download_file_from_api(file_path, local_path, retry=0):
    url = f"{API_BASE}/{file_path}"
    try:
        response = requests.get(url, timeout=30, verify=False, proxies=NO_PROXY)
        response.raise_for_status()
        data = response.json()

        content_base64 = data.get("content", "")
        file_content = None

        if content_base64:
            file_content = base64.b64decode(content_base64)
        else:
            size = data.get("size", 0)
            print(f"   {os.path.basename(file_path)} 大小 {size} 字节，尝试通过 Blob API 下载...")
            if size > 0 and data.get("git_url"):
                file_content = download_file_via_blob(data["git_url"])
            else:
                print(f"   文件无内容且无 git_url，放弃。")
                return False

        if file_content is None or len(file_content) == 0:
            raise ValueError("文件内容为空")

        # JSON check
        if file_path.endswith('.json'):
            try:
                json.loads(file_content.decode('utf-8'))
            except json.JSONDecodeError as e:
                print(f"   下载的文件 JSON 无效: {e}")
                return False

        # save file
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as f:
            f.write(file_content)
        print(f"   已下载: {os.path.basename(local_path)}")
        return True

    except Exception as e:
        print(f"   下载失败: {os.path.basename(local_path)} - {e}")
        if retry < MAX_RETRIES - 1:
            print(f"   将在 {RETRY_DELAY} 秒后重试（{retry+2}/{MAX_RETRIES}）...")
            time.sleep(RETRY_DELAY)
            return download_file_from_api(file_path, local_path, retry + 1)
        return False


def get_remote_version():
    return download_file_from_api(VERSION_FILE, os.path.join(LOCAL_DATA_DIR, VERSION_FILE))


def get_local_version():
    version_path = os.path.join(LOCAL_DATA_DIR, VERSION_FILE)
    if os.path.exists(version_path):
        with open(version_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return None


def update_files():
    print("\n发现新版本，开始更新文件...")
    success = True
    for filename in FILES_TO_UPDATE:
        local_path = os.path.join(LOCAL_DATA_DIR, filename)
        if not download_file_from_api(filename, local_path):
            success = False
    return success


def main():
    print(f"正在下载配队器所需的游戏内资源，计算器等模块所需的其他资源并不包含在内。")
    print(f"当前强制忽略系统代理，并跳过 SSL 验证。")
    print(f"所有文件均通过 GitHub API 下载。")

    print("\n正在检查远程版本...")
    temp_version_path = os.path.join(LOCAL_DATA_DIR, f".temp_{VERSION_FILE}")
    if not download_file_from_api(VERSION_FILE, temp_version_path):
        print("无法获取远程版本，更新终止。")
        return

    with open(temp_version_path, 'r', encoding='utf-8') as f:
        remote_version = f.read().strip()
    print(f"   远程版本: {remote_version}")

    local_version = get_local_version()
    print(f"   本地版本: {local_version if local_version else '无'}")

    if remote_version == local_version:
        print("\n版本一致，无需更新。")
        os.remove(temp_version_path)
        return

    if update_files():
        version_path = os.path.join(LOCAL_DATA_DIR, VERSION_FILE)
        try:
            os.replace(temp_version_path, version_path)
            print(f"   已更新: {VERSION_FILE}")
            print("\n所有文件更新完成！")
        except Exception as e:
            print(f"   版本文件替换失败: {e}")
            print("\nJSON文件已更新，但版本文件保存失败。")
    else:
        print("\n部分文件更新失败，请检查网络后重试。")
        if os.path.exists(temp_version_path):
            os.remove(temp_version_path)


if __name__ == "__main__":
    main()