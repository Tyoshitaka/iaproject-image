


# Iaproject Image Downloader

このプロジェクトは、指定したタグを利用して **IAプロジェクト** から画像をスクレイピングする Python スクリプト `iaproject_image_downloader.py` を提供します。

## 📌 特徴
- 指定したタグを利用して画像を収集
- 自動でフォルダを作成し、画像を保存
- Pythonの `requests` と `BeautifulSoup` を使用

## 🛠 必要なライブラリ
このスクリプトを実行するには、以下のライブラリが必要です。

```bash
pip install requests beautifulsoup4

## 🚀 使い方
python3 iaproject_image_downloader.py <検索タグ> <保存フォルダ>

例：python3 iaproject_image_downloader.py "cat" "./images/cats"



## 📄 ファイル構成
iaproject-image/
├── iaproject_image_downloader.py  # スクレイピングスクリプト
└── README.md                      # このドキュメント


保存後、**Ctrl + X → Y → Enter** で `nano` を終了します。

---

## **✅ 5. Git にファイルを追加**
```bash
git add .

git commit -m "Initial commit: Add iaproject_image_downloader.py and README.md"
