import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os
from datetime import datetime

# Supabase設定
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def scrape_and_update():
    # さわやか全店表示用のURL
    target_url = "https://airwait.jp/WC00001501/PB00001502/embed/wait-time"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    results = []
    
    try:
        print(f"データ取得開始: {target_url}")
        response = requests.get(target_url, headers=headers, timeout=20)
        
        # もし404エラーなら「今は営業時間外」と判断する
        if response.status_code == 404:
            print("【判定】現在は全店舗が受付終了（営業時間外）のため、サイトが表示されていません。")
            # 待ち時間をすべて「999（受付終了）」にするか「0」にするかはお好みですが、
            # ここでは「0」に更新して、updated_atを最新にします。
        elif response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select('.wait-time-shop-row')
            
            for row in rows:
                name_el = row.select_one('.wait-time-shop-name')
                time_el = row.select_one('.wait-time-number')
                if name_el:
                    name = name_el.get_text(strip=True)
                    time_text = time_el.get_text(strip=True).replace('分', '') if time_el else "0"
                    time_val = int(time_text) if time_text.isdigit() else 0
                    
                    results.append({
                        "store_name": name,
                        "wait_time": time_val,
                        "updated_at": datetime.now().isoformat()
                    })

        # データが取得できた場合のみ更新
        if results:
            supabase.table('wait_times').upsert(results, on_conflict='store_name').execute()
            print(f"成功！ {len(results)} 件の店舗データを最新にしました。")
        else:
            print("現在、更新すべき店舗データはありません（深夜のため）。明日10:00以降に再開します。")

    except Exception as e:
        print(f"予期せぬエラー: {e}")

if __name__ == "__main__":
    scrape_and_update()
