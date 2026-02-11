import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os
import datetime

# 1. Supabase設定
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def scrape_and_update():
    # さわやかの待ち時間ページ（AirWAIT）
    target_url = "https://airwait.jp/WC00001501/PB00001502/embed/wait-time?fId=PB00001502"
    
    # ブラウザのふりをする設定
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    results = []
    
    try:
        print(f"データ取得開始: {target_url}")
        response = requests.get(target_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 店舗ごとのブロックを探す
            # ※AirWAITのHTML構造に合わせて調整
            stores = soup.select('.wait-time-shop-row')
            
            for store in stores:
                name_el = store.select_one('.wait-time-shop-name')
                time_el = store.select_one('.wait-time-number')
                
                if name_el:
                    name = name_el.get_text(strip=True)
                    # 待ち時間がない場合や「受付終了」などの場合を考慮
                    wait_time = 0
                    if time_el:
                        time_text = time_el.get_text(strip=True).replace('分', '')
                        if time_text.isdigit():
                            wait_time = int(time_text)
                    
                    print(f"取得: {name} -> {wait_time}分")
                    
                    results.append({
                        "store_name": name,
                        "wait_time": wait_time,
                        # 更新時刻も入れておくと便利です（日本時間ではないですが今はOK）
                        "updated_at": datetime.datetime.now().isoformat()
                    })
        else:
            print(f"サイトにアクセスできませんでした。コード: {response.status_code}")

    except Exception as e:
        print(f"エラー発生: {e}")

    # データが取れたらSupabaseを更新
    if results:
        try:
            # upsert: あれば更新、なければ新規作成
            response = supabase.table('wait_times').upsert(results, on_conflict='store_name').execute()
            print(f"Supabase更新完了！ {len(results)} 店舗のデータを更新しました。")
        except Exception as e:
            print(f"Supabase送信エラー: {e}")
    else:
        print("店舗データが見つかりませんでした。HTML構造が変わった可能性があります。")

if __name__ == "__main__":
    scrape_and_update()
