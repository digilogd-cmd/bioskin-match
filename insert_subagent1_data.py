import sqlite3
import uuid

cosmetics_data = [
    # 설화수
    {"brand": "설화수", "name": "윤조에센스 6세대", "price": 94500, "ingredients": ["정제수", "변성알코올", "부틸렌글라이콜", "베타인", "1,2-헥산다이올", "글리세릴폴리메타크릴레이트", "카보머", "글리세릴카프릴레이트", "호두추출물", "덱스트린", "카카오추출물", "황금추출물", "아데노신", "메틸트라이메티콘", "다이소듐이디티에이", "잔탄검", "셀룰로오스검", "카라기난", "꿀", "마데카소사이드", "지황뿌리추출물", "펜틸렌글라이콜", "소엽맥문동뿌리추출물", "작약뿌리추출물", "마돈나백합비늘줄기추출물", "구기자추출물", "바이오사카라이드검-1", "대추추출물", "연꽃추출물", "칡뿌리추출물", "낫토검", "매실추출물", "표고버섯추출물", "토코페롤", "생강추출물"]},
    {"brand": "설화수", "name": "자음생크림 클래식", "price": 270000, "ingredients": ["정제수", "글리세린", "스쿠알란", "부틸렌글라이콜", "트레할로오스", "메도우폼씨오일"]},
    {"brand": "설화수", "name": "순행클렌징폼", "price": 42000, "ingredients": ["정제수", "포타슘코코일글리시네이트", "다이소듐코코암포다이아세테이트", "코카미도프로필베타인", "아크릴레이트/베헤네스-25메타크릴레이트코폴리머", "피이지-200하이드로제네이티드글리세릴팔메이트"]},
    {"brand": "설화수", "name": "자음수", "price": 65000, "ingredients": ["정제수", "마치현추출물", "구기자추출물", "글리세린", "부틸렌글라이콜", "에탄올", "마돈나백합비늘줄기추출물"]},
    {"brand": "설화수", "name": "자음유액", "price": 70000, "ingredients": ["정제수", "부틸렌글라이콜", "하이드로제네이티드폴리(C6-14올레핀)", "옥틸도데실미리스테이트", "글리세린", "메도우폼씨오일"]},
    
    # 라네즈
    {"brand": "라네즈", "name": "워터뱅크 블루 히알루로닉 인텐시브 크림", "price": 42000, "ingredients": ["정제수", "글리세린", "프로판다이올", "스쿠알란", "세테아릴알코올", "펜타에리스리틸테트라에틸헥사노에이트", "판테놀"]},
    {"brand": "라네즈", "name": "네오 쿠션 매트", "price": 30000, "ingredients": ["정제수", "티타늄디옥사이드", "사이클로펜타실록세인", "메틸트라이메티콘", "에칠헥실메톡시신나메이트"]},
    {"brand": "라네즈", "name": "크림 스킨 리파이너", "price": 28000, "ingredients": ["정제수", "부틸렌글라이콜", "글리세린", "메도우폼씨오일", "1,2-헥산다이올", "폴리글리세릴-10스테아레이트"]},
    {"brand": "라네즈", "name": "립 슬리핑 마스크 EX", "price": 22000, "ingredients": ["다이이소스테아릴말레이트", "하이드로제네이티드폴리아이소부텐", "피토스테릴/이소스테아릴/세틸/스테아릴/베헤닐다이머디리놀리에이트", "폴리우레탄-79", "시어버터"]},
    {"brand": "라네즈", "name": "래디언씨 크림", "price": 29000, "ingredients": ["정제수", "3-O-에틸아스코빅애씨드", "글리세린", "세테아릴알코올", "카프릴릭/카프릭트라이글리세라이드", "프로판다이올"]},
    
    # 닥터자르트
    {"brand": "닥터자르트", "name": "시카페어 인텐시브 수딩 리페어 크림", "price": 50000, "ingredients": ["정제수", "다이프로필렌글라이콜", "세테아릴알코올", "프로판다이올", "폴리글리세릴-3메틸글루코오스다이스테아레이트", "병풀추출물", "세라마이드엔피"]},
    {"brand": "닥터자르트", "name": "세라마이딘 스킨 베리어 모이스처라이징 크림", "price": 48000, "ingredients": ["정제수", "글리세린", "다이프로필렌글라이콜", "세테아릴알코올", "카프릴릭/카프릭트라이글리세라이드", "하이드로제네이티드폴리(C6-14올레핀)", "세라마이드엔피"]},
    {"brand": "닥터자르트", "name": "에브리 선 데이 마일드 선", "price": 20000, "ingredients": ["정제수", "징크옥사이드", "사이클로헥사실록세인", "다이프로필렌글라이콜", "부틸옥틸살리실레이트", "프로판다이올", "티타늄디옥사이드"]},
    {"brand": "닥터자르트", "name": "컨트롤에이 티트리먼트 수딩 스팟", "price": 19000, "ingredients": ["에탄올", "티트리잎추출물", "칼라민", "글리세린", "정제수", "징크옥사이드", "티트리잎오일"]},
    {"brand": "닥터자르트", "name": "더마스크 워터젯 바이탈 하이드라 솔루션", "price": 20000, "ingredients": ["정제수", "글리세린", "부틸렌글라이콜", "에탄올", "판테놀", "베타인", "자일리틸글루코사이드", "소듐하이알루로네이트"]}
]

def insert_data():
    conn = sqlite3.connect('e:/안티그래비티/cosmetic/database/cosmetic.db')
    cursor = conn.cursor()
    
    count = 0
    for p in cosmetics_data:
        brand = p['brand']
        # 먼저 기존 쓰레기 데이터 삭제 방지, 추가만 한다 (혹은 기존 fake 데이터가 있다면 덮어쓰기 위해 brand별 fake 삭제는 나중에)
        pid = f"REAL_{uuid.uuid4().hex[:8].upper()}"
        
        # 카테고리 유추
        cat = '스킨케어'
        if '크림' in p['name']: cat = '크림'
        elif '에센스' in p['name'] or '앰플' in p['name']: cat = '세럼/앰플'
        elif '스킨' in p['name'] or '수' in p['name']: cat = '토너/스킨'
        elif '폼' in p['name'] or '클렌징' in p['name']: cat = '클렌저'
        elif '선' in p['name']: cat = '선케어'
        
        # 럭셔리 여부
        is_lux = 1 if brand in ['설화수'] else 0
        
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
    print(f"Successfully inserted {count} real products from Subagent 1.")

if __name__ == "__main__":
    insert_data()
