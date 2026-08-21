import sqlite3
import random
import uuid

conn = sqlite3.connect('e:/안티그래비티/cosmetic/database/cosmetic.db')
cursor = conn.cursor()

# Get brands with < 10 products
cursor.execute('''
    SELECT brand_name, COUNT(*) 
    FROM products 
    GROUP BY brand_name 
    HAVING COUNT(*) < 10
''')
brands = cursor.fetchall()

luxury_keywords = ['라프레리', '라메르', '시슬리', '겔랑', '끌레드뽀', '톰포드', '아만다', '오휘', '아모레퍼시픽', '숨37', '더히스토리오브후', '발몽', '샹테카이', '바이레도', '조말론', '구찌', '루부탱', '바비브라운', '맥', '나스', '조르지오']

product_templates = [
    ("인텐시브 모이스처 크림", "크림", ["정제수", "글리세린", "시어버터", "세라마이드엔피", "부틸렌글라이콜"]),
    ("어드밴스드 리페어 세럼", "세럼/앰플", ["정제수", "비피다발효용해물", "나이아신아마이드", "판테놀", "소듐하이알루로네이트"]),
    ("카밍 릴리프 토너", "토너/스킨", ["정제수", "병풀추출물", "알란토인", "베타인", "1,2-헥산디올"]),
    ("퍼펙트 글로우 파운데이션", "메이크업", ["정제수", "사이클로펜타실록산", "티타늄디옥사이드", "실리카", "마이카"]),
    ("워터프루프 롱래스팅 아이라이너", "메이크업", ["아크릴레이트코폴리머", "카본블랙", "부틸렌글라이콜", "페녹시에탄올"]),
    ("수딩 알로에 젤", "크림", ["알로에베라잎즙", "글리세린", "카보머", "알지닌", "정제수"]),
    ("비타C 브라이트닝 앰플", "세럼/앰플", ["정제수", "아스코빅애씨드", "나이아신아마이드", "판테놀", "글리세린"]),
    ("젠틀 마일드 폼 클렌저", "클렌저", ["정제수", "미리스틱애씨드", "글리세린", "스테아릭애씨드", "포타슘하이드록사이드"]),
    ("아쿠아 워터 드롭 에센스", "세럼/앰플", ["정제수", "해수", "글리세린", "소듐하이알루로네이트", "부틸렌글라이콜"]),
    ("프로텍트 데일리 선크림", "선케어", ["정제수", "징크옥사이드", "티타늄디옥사이드", "사이클로메치콘", "글리세린"])
]

luxury_product_templates = [
    ("프레스티지 리제너레이팅 크림", "크림", ["정제수", "캐비아추출물", "스쿠알란", "시어버터", "펩타이드"]),
    ("수프림 래디언스 세럼", "세럼/앰플", ["정제수", "다마스크장미꽃수", "트러플추출물", "나이아신아마이드", "판테놀"]),
    ("얼티밋 유스 아이크림", "크림", ["정제수", "인삼추출물", "글리세린", "펩타이드", "아데노신"]),
    ("루미너스 실크 파운데이션", "메이크업", ["정제수", "사이클로헥사실록산", "티타늄디옥사이드", "진주가루", "실리카"]),
    ("벨벳 마뜨 립 컬러", "메이크업", ["옥틸도데칸올", "디카프릴릴카보네이트", "마이카", "카민", "호호바씨오일"]),
    ("골드 리프팅 에센스", "세럼/앰플", ["정제수", "금", "달팽이점액여과물", "소듐하이알루로네이트", "글리세린"]),
    ("럭셔리 펄 바디 로션", "크림", ["정제수", "글리세린", "미네랄오일", "진주추출물", "향료"]),
    ("리뉴얼 엑스폴리에이팅 마스크", "크림", ["정제수", "글리콜산", "락틱애씨드", "알로에베라잎즙", "글리세린"]),
    ("로얄 허니 너리싱 오일", "세럼/앰플", ["호호바씨오일", "아르간커넬오일", "꿀추출물", "토코페롤", "스쿠알란"]),
    ("오키드 임페리얼 토너", "토너/스킨", ["정제수", "난초추출물", "글리세린", "부틸렌글라이콜", "베타인"])
]

total_inserted = 0

for brand_name, count in brands:
    needed = 10 - count
    is_lux = any(lk in brand_name for lk in luxury_keywords)
    
    templates = luxury_product_templates if is_lux else product_templates
    
    for i in range(needed):
        tmpl = templates[i % len(templates)]
        prod_name = f"{brand_name} {tmpl[0]}"
        market_name = prod_name
        cat = tmpl[1]
        ingredients = tmpl[2]
        
        lux_val = 1 if is_lux else 0
        
        if is_lux:
            price = random.randint(8, 45) * 10000
        else:
            price = random.randint(15, 55) * 1000
            
        pid = f"BULK_{uuid.uuid4().hex[:8].upper()}"
        
        cursor.execute('''
            INSERT INTO products 
            (id, brand_name, product_name, market_name, category, is_luxury, data_source, price) 
            VALUES (?, ?, ?, ?, ?, ?, 'BULK_EXPAND', ?)
        ''', (pid, brand_name, prod_name, market_name, cat, lux_val, price))
        
        for ing in ingredients:
            cursor.execute('INSERT OR IGNORE INTO ingredients (name_ko) VALUES (?)', (ing,))
            cursor.execute('SELECT id FROM ingredients WHERE name_ko = ?', (ing,))
            ing_id = cursor.fetchone()[0]
            cursor.execute('INSERT OR IGNORE INTO product_ingredients (product_id, ingredient_id) VALUES (?, ?)', (pid, ing_id))
            
        total_inserted += 1

conn.commit()
conn.close()
print(f"Successfully inserted {total_inserted} products to ensure all brands have >= 10 products.")
