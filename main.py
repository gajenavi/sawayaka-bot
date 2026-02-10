import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os
from dotenv import load_dotenv
import re

load_dotenv()

# Supabaseの設定
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def get_wait_times():
    print("--- データ取得開始 ---")
    target_url = "https://www.genkotsu-hb.com/shop/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(target_url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 修正ポイント：店舗が並んでいる枠（クラス名）を広めに指定
        # さわやかのサイトの「店舗名」と「待ち時間」のセットを探す
        items = soup.select('.shop-list__item, .shopList_item, article')
        
        if not items:
            print("店舗の枠組みが見つかりませんでした。")
            return

        for item in items:
            # 1. 店舗名を探す
            name_el = item.select_one('.shop-list__name, .shopList_name, h3, h4')
            if not name_el: continue
            name = name_el.text.strip()
            
            # 「東部地区」などの見出しを除外
            if "地区" in name or "一覧" in name: continue

            # 2. 待ち時間情報を探す
            wait_el = item.select_one('.shop-list__wait, .shopList_wait, p')
            wait_text = wait_el.text.strip() if wait_el else "0"
            
            # 数字だけをすべて抜き出す
            numbers = re.findall(r'\d+', wait_text)
            wait_time = int(numbers[0]) if len(numbers) > 0 else 0
            wait_groups = int(numbers[1]) if len(numbers) > 1 else 0

            # 3. Supabaseへ保存
            data = {
                "store_name": name,
                "wait_time": wait_time,
                "wait_groups": wait_groups,
                "updated_at": "now()"
            }
            
            try:
                supabase.table("wait_times").upsert(data, on_conflict="store_name").execute()
                status = "🌙 営業時間外/表示なし" if wait_time == 0 else f"🔥 {wait_time}分待ち"
                print(f"[{name}] {status}")
            except Exception as db_err:
                print(f"DB保存エラー ({name}): {db_err}")

        print("--- すべての処理が完了しました ---")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    get_wait_times()