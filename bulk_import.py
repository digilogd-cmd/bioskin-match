import urllib.request
import json
import sqlite3
import time

brands = [
    'dior', 'chanel', 'nyx', 'maybelline', 'clinique', 'loreal', 'revlon', 'covergirl', 'elf',
    'smashbox', 'benefit', 'fenty', 'nars', 'mac', 'glossier', 'colourpop', 'tarte', 'urban decay'
]

# 카테고리별 대표 성분 매핑 (사용자 지시: 대표 성분만 표기되어도 됨)
representative_ingredients = {
    'foundation': ['정제수', '사이클로펜타실록산', '티타늄디옥사이드', '글리세린'],
    'lipstick': ['옥틸도데칸올', '마이카', '실리카', '티타늄디옥사이드'],
    'blush': ['탈크', '징크스테아레이트', '마이카', '카민'],
    'eyeshadow': ['마이카', '탈크', '티타늄디옥사이드', '징크스테아레이트'],
    'eyeliner': ['정제수', '아크릴레이트코폴리머', '카본블랙', '부틸렌글라이콜'],
    'mascara': ['정제수', '밀랍', '카나우바왁스', '스테아릭애씨드'],
    'serum': ['정제수', '부틸렌글라이콜', '글리세린', '나이아신아마이드', '판테놀'],
    'cream': ['정제수', '글리세린', '스쿠알란', '시어버터', '세테아릴알코올'],
    'default': ['정제수', '글리세린', '부틸렌글라이콜']
}

def get_category_and_ingredients(prod_type):
    ptype = str(prod_type).lower()
    if 'foundation' in ptype or 'concealer' in ptype:
        return '메이크업', representative_ingredients['foundation']
    elif 'lipstick' in ptype or 'lip' in ptype:
        return '메이크업', representative_ingredients['lipstick']
    elif 'blush' in ptype or 'bronzer' in ptype:
        return '메이크업', representative_ingredients['blush']
    elif 'eyeshadow' in ptype:
        return '메이크업', representative_ingredients['eyeshadow']
    elif 'eyeliner' in ptype:
        return '메이크업', representative_ingredients['eyeliner']
    elif 'mascara' in ptype:
        return '메이크업', representative_ingredients['mascara']
    elif 'serum' in ptype:
        return '세럼/앰플', representative_ingredients['serum']
    elif 'cream' in ptype:
        return '크림', representative_ingredients['cream']
    else:
        return '메이크업', representative_ingredients['default']

conn = sqlite3.connect('e:/안티그래비티/cosmetic/database/cosmetic.db')
cursor = conn.cursor()

count = 0
for brand in brands:
    if count >= 500:
        break
        
    url = f'http://makeup-api.herokuapp.com/api/v1/products.json?brand={brand}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        print(f'Fetching {brand}...')
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        
        for item in data:
            if count >= 500:
                break
                
            pid = f"BULK_{item['id']}"
            b_name = item.get('brand', brand).capitalize()
            name = item.get('name', 'Unknown')
            market_name = name
            
            cat, ings = get_category_and_ingredients(item.get('product_type'))
            is_lux = 1 if brand in ['dior', 'chanel', 'clinique', 'nars', 'mac', 'smashbox', 'benefit'] else 0
            
            cursor.execute('''
                INSERT OR IGNORE INTO products 
                (id, brand_name, product_name, market_name, category, is_luxury, data_source) 
                VALUES (?, ?, ?, ?, ?, ?, 'GLOBAL_BULK')
            ''', (pid, b_name, name, market_name, cat, is_lux))
            
            for ing in ings:
                cursor.execute('INSERT OR IGNORE INTO ingredients (name_ko) VALUES (?)', (ing,))
                cursor.execute('SELECT id FROM ingredients WHERE name_ko = ?', (ing,))
                ing_id = cursor.fetchone()[0]
                cursor.execute('INSERT OR IGNORE INTO product_ingredients (product_id, ingredient_id) VALUES (?, ?)', (pid, ing_id))
            
            count += 1
        conn.commit()
        time.sleep(1) # Prevent rate limiting
    except Exception as e:
        print(f'API Error for {brand}: {e}')

conn.close()
print(f'Successfully imported {count} items. Total DB size expanded massively.')
