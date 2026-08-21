import urllib.request
import json
import sqlite3

url = 'http://makeup-api.herokuapp.com/api/v1/products.json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
    conn = sqlite3.connect('e:/안티그래비티/cosmetic/database/cosmetic.db')
    cursor = conn.cursor()
    
    count = 0
    for item in data: # Take all products
        pid = f"API_{item['id']}"
        brand = item.get('brand', 'Unknown')
        name = item.get('name', 'Unknown')
        market_name = name
        category = '크림' if 'cream' in str(item.get('product_type')).lower() else '세럼/앰플'
        
        # Insert product
        cursor.execute('''
            INSERT OR IGNORE INTO products 
            (id, brand_name, product_name, market_name, category, is_luxury, data_source) 
            VALUES (?, ?, ?, ?, ?, ?, 'MAKEUP_API')
        ''', (pid, brand, name, market_name, category, 1))
        
        # Mock ingredients for now since makeup API lacks full lists
        ingredients = ['글리세린', '정제수', '부틸렌글라이콜']
        for ing in ingredients:
            cursor.execute('INSERT OR IGNORE INTO ingredients (name_ko) VALUES (?)', (ing,))
            cursor.execute('SELECT id FROM ingredients WHERE name_ko = ?', (ing,))
            ing_id = cursor.fetchone()[0]
            cursor.execute('INSERT OR IGNORE INTO product_ingredients (product_id, ingredient_id) VALUES (?, ?)', (pid, ing_id))
            
        count += 1
        
    conn.commit()
    conn.close()
    print(f'Successfully imported {count} items from Makeup API.')
except Exception as e:
    print('API Error:', e)
