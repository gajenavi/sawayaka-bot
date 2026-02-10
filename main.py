import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os

# 1. Supabaseの設定（GitHub Secretsから読み込み）
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def scrape_and_update():
    # 2. さわやか公式サイト（全店一括表示ページ）
    target_url = "https://airwait.jp/WC00001501/PB00001502/embed/wait-time?fId=PB00001502"
    
    try:
        response = requests.get(target_url)
        response.raise_for_status() # 通信エラーがあればここで止める
        soup = BeautifulSoup(response.text, 'html.parser')

        # 3. 店舗情報を抜き出す（サイトの構造に合わせて解析）
        # ※AirWAITの構造に基づいた抽出処理
        stores = soup.select('.wait-time-shop-row') # 店舗ごとの行を取得
        
        results = []
        for store in stores:
            name_el = store.select_one('.wait-time-shop-name')
            time_el = store.select_one('.wait-time-number')
            
            if name_el and time_el:
                name = name_el.get_text(strip=True)
                # 「120分」から数字だけ抜き出す
                time_str = time_el.get_text(strip=True).replace('分', '')
                time_val = int(time_str) if time_str.isdigit() else 0
                
                results.append({
                    "store_name": name,
                    "wait_time": time_val
                })

        # 4. Supabaseにデータを送る
        if results:
            # wait_timesテーブルにまとめて保存（store_nameが同じなら上書き）
            response = supabase.table('wait_times').upsert(results, on_conflict='store_name').execute()
            print(f"成功！ {len(results)} 件の店舗データを更新しました。")
        else:
            print("店舗データが見つかりませんでした。サイトの構造が変わった可能性があります。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise e # エラーをわざと発生させてGitHubに通知する

if __name__ == "__main__":
    scrape_and_update()
