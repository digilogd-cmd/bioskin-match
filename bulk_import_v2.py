import urllib.request
import json
import sqlite3
import time

more_brands = [
    'milani', 'almay', 'physicians formula', 'wet n wild', 'pacifica', 
    'stila', 'zorah', "burt's bees", 'butter london', 'cargo cosmetics', 
    'deciem', 'iman', 'suncoat'
]

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

for brand in more_brands:
    url = f'http://makeup-api.herokuapp.com/api/v1/products.json?brand={brand.replace(" ", "+")}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        
        for item in data:
            pid = f"BULK_V2_{item['id']}"
            b_name = item.get('brand', brand).capitalize()
            name = item.get('name', 'Unknown')
            cat, ings = get_category_and_ingredients(item.get('product_type'))
            
            cursor.execute('''
                INSERT OR IGNORE INTO products 
                (id, brand_name, product_name, market_name, category, is_luxury, data_source) 
                VALUES (?, ?, ?, ?, ?, 0, 'GLOBAL_BULK_V2')
            ''', (pid, b_name, name, name, cat))
            
            for ing in ings:
                cursor.execute('INSERT OR IGNORE INTO ingredients (name_ko) VALUES (?)', (ing,))
                cursor.execute('SELECT id FROM ingredients WHERE name_ko = ?', (ing,))
                ing_id = cursor.fetchone()[0]
                cursor.execute('INSERT OR IGNORE INTO product_ingredients (product_id, ingredient_id) VALUES (?, ?)', (pid, ing_id))
            
            count += 1
        conn.commit()
        time.sleep(1)
    except Exception as e:
        print(f'Error on {brand}: {e}')

conn.close()
print(f'Inserted {count} items from additional global brands.')
