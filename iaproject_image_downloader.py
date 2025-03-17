# -*- coding: utf-8 -*-

import os
import time
import requests
import imghdr
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# **設定**
TAGS = ["救世主", "ソプスク", "ナッペ", "パラクラ", "オルダブ", "同じ穴", "同じ穴の僕ら", "ソプスク"]  # ← 短縮版（本番はリストそのままでOK）
SAVE_FOLDER = "downloaded_images"
ACCESS_TOKEN = "ここにトークンを挿入"
MAX_WORKERS = 10  # 並列処理のスレッド数

# **HTTPヘッダー**
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}
first_error_tag = None  # 最初にエラーになったタグを記録

# **画像保存フォルダを作成**
os.makedirs(SAVE_FOLDER, exist_ok=True)

def fetch_image_urls(tag):
    """指定したタグでAPIから画像URLを取得"""
    global first_error_tag
    api_url = f"https://apiv3.iachara.com/v3/charasheet/tag?tag={tag}&limit=100"

    try:
        response = requests.get(api_url, headers=HEADERS)

        if response.status_code != 200:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"⚠ [{now}] タグ '{tag}' の画像取得で APIエラー: {response.status_code} - {response.text}")
            if first_error_tag is None:
                first_error_tag = tag
            return tag, []

        data = response.json()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ [{now}] タグ '{tag}' の取得データ数: {len(data)}")

        image_urls = [icon["url"] for entry in data for icon in entry.get("data", {}).get("profile", {}).get("icons", []) if "url" in icon]

        print(f"🎯 [{now}] タグ '{tag}' の取得した画像URL数: {len(image_urls)}")
        return tag, image_urls

    except requests.exceptions.RequestException as e:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"⚠ [{now}] タグ '{tag}' - 通信エラー: {e}")
        if first_error_tag is None:
            first_error_tag = tag
        return tag, []

def download_image(url, retries=3):
    """画像をダウンロード (1MB以上のみ & 拡張子を自動判別)"""
    img_name = os.path.basename(url)
    img_path = os.path.join(SAVE_FOLDER, img_name)

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, stream=True)
            if response.status_code == 200:
                content_length = response.headers.get('Content-Length')
                size_kb = int(content_length) / 1024 if content_length else len(response.content) / 1024
                print(f"✅ {url} - サイズ {size_kb:.2f} KB")
                if size_kb >= 1024:
                    with open(img_path, "wb") as file:
                        for chunk in response.iter_content(1024):
                            file.write(chunk)
                    if not os.path.exists(img_path):
                        print(f"⚠ ダウンロード失敗: {url}")
                        continue
                    try:
                        ext = imghdr.what(img_path)
                        if ext:
                            new_img_path = f"{img_path}.{ext}"
                            os.rename(img_path, new_img_path)
                            print(f"📥 ダウンロード完了: {new_img_path}")
                        else:
                            print(f"⚠ 拡張子不明: {img_path}")
                    except FileNotFoundError:
                        print(f"🚨 ファイルが存在しません: {img_path}")
                else:
                    print(f"⏩ {url} - サイズ {size_kb:.2f} KB (小さいためスキップ)")
                return
            else:
                print(f"⚠ {url} - HTTPエラー: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠ {url} - ダウンロードエラー: {e}")
        if attempt < retries - 1:
            print(f"🔄 リトライ ({attempt+1}/{retries})")
            time.sleep(2)
    print(f"❌ ダウンロード失敗: {url}")

print("\n🔍 タグごとの画像URLを並列取得中...")
tag_image_map = {}
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    future_to_tag = {executor.submit(fetch_image_urls, tag): tag for tag in TAGS}
    for future in as_completed(future_to_tag):
        tag, image_urls = future.result()
        tag_image_map[tag] = image_urls

print("\n📥 画像を並列ダウンロード中...")
download_futures = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    for tag, image_urls in tag_image_map.items():
        for img_url in image_urls:
            future = executor.submit(download_image, img_url)
            download_futures.append(future)
    for future in as_completed(download_futures):
        future.result()

if first_error_tag:
    print(f"\n🚨 最初にエラーになったタグ: {first_error_tag}")

print("\n✅ すべてのダウンロードが完了しました！")
