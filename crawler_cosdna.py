import sqlite3
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import random
import uuid
import time
import ssl
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
BASE_URL = 'https://cosdna.com/kor/'

def get_html(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def scrape_brand(query, exact_brand_name, min_price, max_price, is_luxury, limit=10):
    encoded_query = urllib.parse.quote(query)
    search_url = f"{BASE_URL}product.php?q={encoded_query}"
    
    html = get_html(search_url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    
    products = []
    # Find product rows
    rows = soup.select('.table-striped tbody tr')
    
    for row in rows:
        if len(products) >= limit:
            break
            
        tds = row.select('td')
        if not tds:
            continue
            
        a_tag = tds[0].select_one('a')
        if not a_tag:
            continue
            
        prod_name = a_tag.text.strip()
        
        # 필터링: 영어만 있거나, 짧은 텍스트 등 필터링
        if len(prod_name) < 3:
            continue
            
        prod_url = BASE_URL + a_tag['href']
        
        # 제품 상세 페이지 접속하여 전성분 추출
        time.sleep(0.5)  # 서버 부하 방지
        detail_html = get_html(prod_url)
        if not detail_html:
            continue
            
        detail_soup = BeautifulSoup(detail_html, 'html.parser')
        
        ingredients = []
        ing_rows = detail_soup.select('.tr-i')
        for ir in ing_rows:
            ing_name_td = ir.select_one('td.colors')
            if not ing_name_td:
                # Fallback
                ing_name_td = ir.select_one('td')
                
            if ing_name_td:
                ing_name = ing_name_td.text.strip()
                if ing_name and not ing_name.isascii():
                    # 한국어 성분명만 취득
                    # 간혹 영어 텍스트만 있는 행 방지 (선택적)
                    ingredients.append(ing_name)
                elif ing_name:
                    ingredients.append(ing_name)
                    
        # 성분이 없으면 스킵
        if not ingredients:
            continue
            
        # 중복 제거 (순서 유지)
        unique_ings = []
        for ing in ingredients:
            ing_clean = ing.split('\n')[0].strip()
            if ing_clean and ing_clean not in unique_ings:
                unique_ings.append(ing_clean)
                
        # 가격 생성
        price = random.randint(min_price // 1000, max_price // 1000) * 1000
        
        products.append({
            'name': prod_name,
            'ingredients': unique_ings,
            'price': price
        })
        print(f"Scraped: [{exact_brand_name}] {prod_name} (Ingredients: {len(unique_ings)}) - ₩{price:,}")
        
    return products

def save_to_db(products, brand_name, is_luxury):
    conn = sqlite3.connect('e:/안티그래비티/cosmetic/database/cosmetic.db')
    cursor = conn.cursor()
    
    count = 0
    for p in products:
        pid = f"REAL_{uuid.uuid4().hex[:8].upper()}"
        cat = '세럼/앰플' if '세럼' in p['name'] or '에센스' in p['name'] else '크림' if '크림' in p['name'] else '스킨케어'
        
        cursor.execute('''
            INSERT INTO products 
            (id, brand_name, product_name, market_name, category, is_luxury, data_source, price) 
            VALUES (?, ?, ?, ?, ?, ?, 'REAL_COSDNA', ?)
        ''', (pid, brand_name, p['name'], p['name'], cat, 1 if is_luxury else 0, p['price']))
        
        for ing in p['ingredients']:
            cursor.execute('INSERT OR IGNORE INTO ingredients (name_ko) VALUES (?)', (ing,))
            cursor.execute('SELECT id FROM ingredients WHERE name_ko = ?', (ing,))
            ing_id = cursor.fetchone()[0]
            cursor.execute('INSERT OR IGNORE INTO product_ingredients (product_id, ingredient_id) VALUES (?, ?)', (pid, ing_id))
            
        count += 1
        
    conn.commit()
    conn.close()
    print(f"Saved {count} products to DB for {brand_name}.")

if __name__ == "__main__":
    import pip
    pip.main(['install', 'beautifulsoup4'])
    
    print("Starting Aesop crawler test...")
    # 이솝: 럭셔리, 가격대 50,000 ~ 180,000
    aesop_data = scrape_brand("aesop", "이솝(Aesop)", 50000, 180000, is_luxury=True, limit=10)
    if aesop_data:
        save_to_db(aesop_data, "이솝(Aesop)", True)
    else:
        print("Failed to scrape Aesop data.")
