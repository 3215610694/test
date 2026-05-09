#!/usr/bin/env python3
"""
m3u8 批量下载器 - 基于 N_m3u8DL-RE (最终稳定版)
修复 URL 截断问题，使用正则提取完整链接。
"""

import os
import subprocess
import shlex
import re

# ========== 用户配置区域 ==========

# 【模式选择】
# "inline" : 直接在下方的 CURL_COMMANDS 多行字符串中粘贴 curl 命令
# "file"   : 从指定的文件读取 curl 命令（每行一个）
MODE = "inline"   # 或 "file"

# ---------- 内联模式配置 (MODE="inline") ----------
# 在这里粘贴你的所有 curl 命令（每行一个完整的 curl 命令）
CURL_COMMANDS = """
curl -X GET 'https://k.zl94skhn.work/api/m3u8/decode/authPath?auth_key=1775292053-126589027-2-8369cb91ae04f96016eaa2aeff7f0a3e&path=jpg/20260403/u3/43/ci/na/e3bb196ed91042899184420335ce7879.m3u8' -H 'User-Agent: Mozilla/5.0 (Linux; Android 12; HBP-AL00 Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/110.0.5481.154 Mobile Safari/537.36;SuiRui/twitter/ver=1.6.9' -H 'Connection: Keep-Alive' -H 'Accept-Encoding: gzip' -H 'aut: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyNjU4OTAyNyIsImlhdCI6MTc3MzMyNDE0NSwibmJmIjoxNzczMzI0MTQ1LCJleHAiOjE5MzEwMDQxNDV9.0f1kzuiPX0tiaysN-NvcrT_PN2X3Ayt9GiELmucvjHI' -H 's: 1e5666919921cc92c6890946008f3988' -H 't: 1775292051613'
curl -X GET 'https://k.zl94skhn.work/api/m3u8/decode/authPath?auth_key=1775292068-126589027-2-f27b42a7d45c19e950078fe5e851f5fa&path=jpd/20260309/po/37/fr/hj/f933067658ab4a69ab57eb7d93e6fefc.m3u8' -H 'User-Agent: Mozilla/5.0 (Linux; Android 12; HBP-AL00 Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/110.0.5481.154 Mobile Safari/537.36;SuiRui/twitter/ver=1.6.9' -H 'Connection: Keep-Alive' -H 'Accept-Encoding: gzip' -H 'aut: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyNjU4OTAyNyIsImlhdCI6MTc3MzMyNDE0NSwibmJmIjoxNzczMzI0MTQ1LCJleHAiOjE5MzEwMDQxNDV9.0f1kzuiPX0tiaysN-NvcrT_PN2X3Ayt9GiELmucvjHI' -H 's: 1e5666919921cc92c6890946008f3988' -H 't: 1775292066543'
""".strip()

# ---------- 文件模式配置 (MODE="file") ----------
# 将 curl 命令保存为文本文件（每行一个），指定路径
CURL_FILE_PATH = r"C:\工具总文件夹\curl_commands.txt"

# ---------- 通用配置 ----------
SAVE_DIR = r"C:\工具总文件夹\视频下载\nm3u8"   # 保存目录
THREADS = 8                                   # 下载线程数
KEY = None                                     # 密钥（可选）
BINARY_PATH = "N_m3u8DL-RE"                    # 可执行文件路径
OUTPUT_NAME_PATTERN = "video_{idx}"            # 文件名模板，可用 {idx} 序号
# ======================================================

def parse_curl_to_headers_and_url(curl_cmd):
    """
    从 curl 命令中提取 URL 和所有请求头。
    改进：使用正则提取 URL，避免换行截断问题。
    返回 (url, headers_dict)
    """
    # 1. 用正则提取第一个 http:// 或 https:// 链接（允许链接中包含 ? & = 等字符）
    url_match = re.search(r'https?://[^\s\'"]+', curl_cmd)
    url = url_match.group(0) if url_match else None
    if url:
        # 去除可能的尾随引号或括号
        url = url.rstrip('\'")')

    # 2. 提取请求头（使用 shlex 分割）
    headers = {}
    try:
        tokens = shlex.split(curl_cmd)
    except Exception as e:
        print(f"curl 命令解析失败: {e}\n{curl_cmd}")
        return url, headers

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in ('-H', '--header'):
            if i + 1 < len(tokens):
                header_line = tokens[i+1]
                if ':' in header_line:
                    key, value = header_line.split(':', 1)
                    headers[key.strip()] = value.strip()
                else:
                    print(f"警告: 无法解析请求头: {header_line}")
                i += 1
        i += 1

    return url, headers

def download_single(url, headers, output_name):
    """单个下载任务"""
    if not url:
        print(f"错误: URL 为空，跳过下载 {output_name}")
        return

    cmd = [
        BINARY_PATH,
        url,
        "--save-name", output_name,
        "--save-dir", SAVE_DIR,
        "--thread-count", str(THREADS),
    ]
    for k, v in headers.items():
        cmd.append("-H")
        cmd.append(f"{k}: {v}")
    if KEY:
        cmd.append("--key")
        cmd.append(KEY)

    print(f"\n开始下载: {output_name}")
    print(" ".join(cmd))
    print("=" * 60)

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="")
        process.wait()
        if process.returncode == 0:
            print(f"\n✅ {output_name} 下载完成！")
        else:
            print(f"\n❌ {output_name} 下载失败，返回码 {process.returncode}")
    except KeyboardInterrupt:
        print("\n用户中断下载")
        process.terminate()
        raise
    except Exception as e:
        print(f"发生错误: {e}")

def main():
    os.makedirs(SAVE_DIR, exist_ok=True)

    # 获取 curl 命令列表
    if MODE == "inline":
        # 过滤空行和纯注释行（以#开头）
        curl_lines = []
        for line in CURL_COMMANDS.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                curl_lines.append(line)
    elif MODE == "file":
        with open(CURL_FILE_PATH, 'r', encoding='utf-8') as f:
            curl_lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        print("未知模式，请设置 MODE 为 'inline' 或 'file'")
        return

    if not curl_lines:
        print("没有找到任何 curl 命令，退出。")
        return

    print(f"共发现 {len(curl_lines)} 个 curl 命令，开始解析...")

    tasks = []
    for idx, curl in enumerate(curl_lines):
        url, headers = parse_curl_to_headers_and_url(curl)
        if not url:
            print(f"第 {idx+1} 个 curl 命令解析失败，跳过")
            continue
        tasks.append((url, headers, idx))

    print(f"成功解析 {len(tasks)} 个任务，开始下载...")

    for url, headers, idx in tasks:
        output_name = OUTPUT_NAME_PATTERN.format(idx=idx+1)
        download_single(url, headers, output_name)

if __name__ == "__main__":
    main()