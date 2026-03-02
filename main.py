import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os
from datetime import datetime
import re

# 1. Supabase設定
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def scrape_and_update():
    # 埋め込み用ではなく、店舗一覧が見えるURLを使用
    target_url = "https://airwait.jp/WC00001501/PB00001502/embed/wait-time"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
    }
    
    results = []
    
    try:
        print(f"アクセス開始: {target_url}")
        response = requests.get(target_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"サイトアクセス失敗。コード: {response.status_code} (深夜のため受付終了の可能性が高いです)")
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 全店舗の行を取得
            rows = soup.find_all(class_='wait-time-shop-row')
            
            for row in rows:
                name_tag = row.find(class_='wait-time-shop-name')
                time_tag = row.find(class_='wait-time-number')
                
                if name_tag:
                    store_name = name_tag.get_text(strip=True)
                    # 待ち時間を数字だけにする（「120分」→ 120 / 「受付終了」→ 0）
                    time_text = time_tag.get_text(strip=True) if time_tag else "0"
                    # 数字以外（分、名など）を消して、数字だけ取り出す
                    time_val = 0
                    nums = re.findall(r'\d+', time_text)
                    if nums:
                        time_val = int(nums[0])
                    
                    results.append({
                        "store_name": store_name,
                        "wait_time": time_val,
                        "updated_at": datetime.now().isoformat()
                    })

        # --- デバッグ用：データが0件の時だけテストデータを入れる ---
        if not results:
            print("本物のデータが見つかりません。深夜の受付終了時間帯です。")
            # 動作確認のため、1件だけ「夜間テスト」という名前でデータを送ります
            results.append({
                "store_name": "夜間テスト（明日11時に本物に変わります）",
                "wait_time": 0,
                "updated_at": datetime.now().isoformat()
            })

        # Supabaseへ送信
        if results:
            supabase.table('wait_times').upsert(results, on_conflict='store_name').execute()
            print(f"Supabaseへ {len(results)} 件送信しました。")

    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    scrape_and_update()
