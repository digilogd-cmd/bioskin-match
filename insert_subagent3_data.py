import sqlite3
import uuid

products_data = [
    # --- 코스알엑스 (COSRX) ---
    {
        "brand": "코스알엑스",
        "name": "어드벤스드 스네일 96 뮤신 파워 에센스",
        "price": 23000,
        "ingredients": ["달팽이점액여과물", "베타인", "부틸렌글라이콜", "1,2-헥산다이올", "소듐폴리아크릴레이트", "페녹시에탄올", "소듐하이알루로네이트", "알란토인", "카보머", "판테놀", "알지닌", "정제수"]
    },
    {
        "brand": "코스알엑스",
        "name": "풀핏 프로폴리스 시너지 토너",
        "price": 22000,
        "ingredients": ["정제수", "프로폴리스추출물", "꿀추출물", "부틸렌글라이콜", "1,2-헥산다이올", "글리세린", "베타인", "계수나무씨추출물", "판테놀"]
    },
    {
        "brand": "코스알엑스",
        "name": "원스텝 오리지널 블레미쉬 모공 클리어 패드",
        "price": 24000,
        "ingredients": ["흰버드나무껍질수", "부틸렌글라이콜", "글리세린", "1,2-헥산다이올", "베타인살리실레이트", "판테놀", "알란토인", "티트리잎오일", "소듐하이알루로네이트", "아데노신"]
    },
    {
        "brand": "코스알엑스",
        "name": "어드밴스드 더 비타민 씨 23 세럼",
        "price": 23000,
        "ingredients": ["정제수", "아스코빅애씨드", "프로판다이올", "다이메티콘", "트로메타민", "판테놀", "에칠아스코빌에텔", "스쿠알란", "카페인"]
    },
    {
        "brand": "코스알엑스",
        "name": "더 6 펩타이드 스킨 부스터 세럼",
        "price": 23000,
        "ingredients": ["정제수", "다이프로필렌글라이콜", "글리세린", "펜틸렌글라이콜", "1,2-헥산다이올", "나이아신아마이드", "아세틸헥사펩타이드-8", "카퍼트라이펩타이드-1"]
    },
    # --- 토리든 (Torriden) ---
    {
        "brand": "토리든",
        "name": "다이브인 저분자 히알루론산 세럼",
        "price": 22000,
        "ingredients": ["정제수", "부틸렌글라이콜", "글리세린", "다이프로필렌글라이콜", "1,2-헥산다이올", "판테놀", "소듐하이알루로네이트", "하이드롤라이즈드하이알루로닉애씨드", "알란토인", "마데카소사이드"]
    },
    {
        "brand": "토리든",
        "name": "다이브인 저분자 히알루론산 수딩 크림",
        "price": 24000,
        "ingredients": ["정제수", "부틸렌글라이콜", "글리세린", "1,2-헥산다이올", "하이드로제네이티드다이데센", "알란토인", "트레할로오스", "판테놀", "소듐하이알루로네이트"]
    },
    {
        "brand": "토리든",
        "name": "다이브인 저분자 히알루론산 토너",
        "price": 21000,
        "ingredients": ["정제수", "부틸렌글라이콜", "다이프로필렌글라이콜", "1,2-헥산다이올", "글리세린", "베타인", "알란토인", "판테놀", "소듐하이알루로네이트"]
    },
    {
        "brand": "토리든",
        "name": "솔리드인 세라마이드 립 에센스",
        "price": 7000,
        "ingredients": ["폴리아이소부텐", "페트롤라툼", "다이아이소스테아릴말레이트", "호호바씨오일", "시어버터", "솔비탄세스퀴올리에이트", "마카다미아씨오일", "올리브오일", "세라마이드엔피"]
    },
    {
        "brand": "토리든",
        "name": "밸런스풀 시카 진정 세럼",
        "price": 23000,
        "ingredients": ["정제수", "부틸렌글라이콜", "글리세린", "다이프로필렌글라이콜", "1,2-헥산다이올", "병풀추출물", "마데카소사이드", "아시아티코사이드", "아시아틱애씨드", "마데카식애씨드", "판테놀"]
    },
    # --- 클리오 (CLIO) ---
    {
        "brand": "클리오",
        "name": "킬 커버 더 뉴 파운웨어 쿠션",
        "price": 36000,
        "ingredients": ["정제수", "사이클로펜타실록세인", "티타늄디옥사이드", "에칠헥실메톡시신나메이트", "부틸렌글라이콜", "에칠헥실살리실레이트", "나이아신아마이드", "세틸에틸헥사노에이트", "실리카"]
    },
    {
        "brand": "클리오",
        "name": "프로 아이 팔레트 에어",
        "price": 34000,
        "ingredients": ["탤크", "마이카", "합성플루오르플로고파이트", "칼슘티타늄보로실리케이트", "다이메티콘", "티타늄디옥사이드", "적색산화철", "황색산화철", "흑색산화철", "실리카"]
    },
    {
        "brand": "클리오",
        "name": "킬 래쉬 수퍼프루프 마스카라",
        "price": 18000,
        "ingredients": ["아이소도데케인", "다이스테아다이모늄헥토라이트", "덱스트린팔미테이트", "트라이메틸실록시실리케이트", "마이크로크리스탈린왁스", "세레신"]
    },
    {
        "brand": "클리오",
        "name": "샤프 쏘 심플 워터프루프 펜슬 라이너",
        "price": 10000,
        "ingredients": ["트라이메틸실록시실리케이트", "사이클로펜타실록세인", "적색산화철", "흑색산화철", "마이카", "합성왁스", "아이소도데케인", "카나우바왁스"]
    },
    {
        "brand": "클리오",
        "name": "크리스탈 글램 틴트",
        "price": 18000,
        "ingredients": ["정제수", "다이아이소스테아릴말레이트", "비스-다이글리세릴폴리아실아디페이트-2", "다이페닐실록시페닐트라이메티콘", "글리세린", "펜틸렌글라이콜", "폴리솔베이트60"]
    }
]

def insert_data():
    conn = sqlite3.connect('e:/안티그래비티/cosmetic/database/cosmetic.db')
    cursor = conn.cursor()
    
    count = 0
    for p in products_data:
        brand = p['brand']
        pid = f"REAL_{uuid.uuid4().hex[:8].upper()}"
        
        cat = '스킨케어'
        if '크림' in p['name']: cat = '크림'
        elif '에센스' in p['name'] or '앰플' in p['name'] or '세럼' in p['name']: cat = '세럼/앰플'
        elif '스킨' in p['name'] or '수' in p['name'] or '토너' in p['name'] or '패드' in p['name']: cat = '토너/스킨'
        elif '폼' in p['name'] or '클렌징' in p['name']: cat = '클렌저'
        elif '선' in p['name']: cat = '선케어'
        else: cat = '메이크업'
        
        is_lux = 0
        
        cursor.execute('''
            INSERT INTO products 
            (id, brand_name, product_name, market_name, category, is_luxury, data_source, price) 
            VALUES (?, ?, ?, ?, ?, ?, 'WEB_VERIFIED', ?)
        ''', (pid, brand, p['name'], p['name'], cat, is_lux, p['price']))
        
        for ing in p['ingredients']:
            cursor.execute('INSERT OR IGNORE INTO ingredients (name_ko) VALUES (?)', (ing,))
            cursor.execute('SELECT id FROM ingredients WHERE name_ko = ?', (ing,))
            row = cursor.fetchone()
            if row:
                ing_id = row[0]
                cursor.execute('INSERT OR IGNORE INTO product_ingredients (product_id, ingredient_id) VALUES (?, ?)', (pid, ing_id))
            
        count += 1
        
    conn.commit()
    conn.close()
    print(f"Successfully inserted {count} real products from Subagent 3.")

if __name__ == "__main__":
    insert_data()
