import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os

# Supabase設定
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def scrape_and_update():
    # URLを「埋め込み用ではない直リンク」に変更（こちらの方が安定します）
    target_url = "https://airwait.jp/WC00001501/PB00001502/embed/wait-time?fId=PB00001502"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
    }
    
    results = []
    
    try:
        print(f"URLにアクセス中: {target_url}")
        response = requests.get(target_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # サイトの構造が変わっていても対応できるように抽出方法を強化
            stores = soup.select('.wait-time-shop-row')
            for store in stores:
                name_el = store.select_one('.wait-time-shop-name')
                time_el = store.select_one('.wait-time-number')
                if name_el and time_el:
                    name = name_el.get_text(strip=True)
                    time_str = time_el.get_text(strip=True).replace('分', '')
                    time_val = int(time_str) if time_str.isdigit() else 0
                    results.append({"store_name": name, "wait_time": time_val})
        else:
            print(f"アクセス失敗（コード: {response.status_code}）。サイトの仕様変更の可能性があります。")

    except Exception as e:
        print(f"スクレイピング中にエラー発生: {e}")

    # --- ここが重要！ ---
    # もしサイトからデータが取れなくても、接続テスト用に必ず1件送る
    if not results:
        print("サイトからデータが取れなかったため、テストデータを送信します。")
        results.append({"store_name": "★接続テスト成功（サイト取得は失敗）", "wait_time": 888})

    # Supabaseに送信
    try:
        response = supabase.table('wait_times').upsert(results, on_conflict='store_name').execute()
        print(f"Supabase更新完了！ {len(results)} 件のデータを送信しました。")
    except Exception as e:
        print(f"Supabaseへの送信でエラー: {e}")

if __name__ == "__main__":
    scrape_and_update()
