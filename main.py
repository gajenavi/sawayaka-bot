import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Supabaseの設定
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def scrape_and_update():
    # 2. さわやか公式サイトからデータ取得
    target_url = "https://airwait.jp/WC00001501/PB00001502/embed/wait-time" # 実際のURLに書き換えてください
    response = requests.get(target_url)
    # ※ここには以前作成したスクレイピングのロジックが入ります
    
    # --- 中略（店舗名と待ち時間を取得する処理） ---
    
    # 3. データの保存（ここを修正！）
    # テスト用に1件データを送ってみます
    data = {
        "store_name": "御殿場インター店", # 実際はスクレイピングした変数
        "wait_time": 120                 # 実際はスクレイピングした変数
    }

    # 一旦中身を空にしてから入れる、もしくは更新する
    # 今回はシンプルに「upsert（あれば更新、なければ挿入）」を使います
    response = supabase.table('wait_times').upsert(data, on_conflict='store_name').execute()
    print("Supabase更新完了:", response)

if __name__ == "__main__":
    scrape_and_update()
