import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os

# Supabase設定
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def scrape_and_update():
    # URLを一番シンプルな形に戻します
    target_url = "https://airwait.jp/WC00001501/PB00001502/embed/wait-time"
    
    # ロボットだとバレないように「ブラウザのふり」をする設定
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"URLにアクセス中: {target_url}")
        # headersを追加してアクセス
        response = requests.get(target_url, headers=headers)
        
        if response.status_code != 200:
            print(f"アクセス失敗。ステータスコード: {response.status_code}")
            # 万が一失敗しても、Supabaseとの接続テスト用にダミーを送る
            results = [{"store_name": "接続テスト成功（サイト取得失敗）", "wait_time": 0}]
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            # AirWAITの店舗リストのクラス名を確認
            stores = soup.select('.wait-time-shop-row')
            results = []
            for store in stores:
                name_el = store.select_one('.wait-time-shop-name')
                time_el = store.select_one('.wait-time-number')
                if name_el and time_el:
                    name = name_el.get_text(strip=True)
                    time_str = time_el.get_text(strip=True).replace('分', '')
                    time_val = int(time_str) if time_str.isdigit() else 0
                    results.append({"store_name": name, "wait_time": time_val})

        if results:
            # Supabaseへ送信
            response = supabase.table('wait_times').upsert(results, on_conflict='store_name').execute()
            print(f"完了！ {len(results)} 件のデータを更新しました。")

    except Exception as e:
        print(f"エラー発生: {e}")

if __name__ == "__main__":
    scrape_and_update()
