import sqlite3

extra_data = [
    # 아이허브 (iHerb) 직구 인기템
    ('IHERB_001', '유세린', 'Q10 안티링클 페이스 크림', '아이허브 유세린', '크림', 0, '정제수, 글리세린, 유비퀴논, 비타민E, 마카다미아씨오일', 'IHERB', 0),
    ('IHERB_002', '코스알엑스', '어드밴스드 스네일 96 뮤신 파워 에센스', '달팽이 에센스', '세럼/앰플', 0, '달팽이점액여과물, 베타인, 부틸렌글라이콜, 1,2-헥산디올, 소듐하이알루로네이트', 'IHERB', 0),
    ('IHERB_003', '나우푸드', '스위트 아몬드 오일 100%', '나우푸드 아몬드오일', '페이셜오일', 0, '스위트아몬드오일', 'IHERB', 0),
    ('IHERB_004', '디퍼린', '아다팔렌 겔 0.1% 여드름 치료제', '디퍼린 겔', '세럼/앰플', 0, '아다팔렌, 프로필렌글라이콜, 카보머, 정제수', 'IHERB', 1),
    ('IHERB_005', '세라비', '모이스춰라이징 로션', '세라비 로션', '크림', 0, '정제수, 글리세린, 세라마이드엔피, 콜레스테롤, 피토스핑고신, 소듐하이알루로네이트', 'IHERB', 0),

    # 백화점 명품 라인업
    ('DEPT_001', '샤넬', '수블리마지 라 크렘', '샤넬 수블리마지', '크림', 1, '정제수, 글리세린, 스쿠알란, 바닐라열매추출물, 시어버터', 'DEPT_STORE', 0),
    ('DEPT_002', '라메르', '크렘 드 라 메르', '라메르 크림', '크림', 1, '해조추출물, 미네랄오일, 페트롤라툼, 글리세린, 마카다미아씨오일', 'DEPT_STORE', 0),
    ('DEPT_003', 'SK-II', '페이셜 트리트먼트 에센스', '피테라 에센스', '토너/스킨', 1, '갈락토미세스발효여과물, 부틸렌글라이콜, 펜틸렌글라이콜, 정제수', 'DEPT_STORE', 0),
    ('DEPT_004', '겔랑', '아베이 로얄 어드밴스드 유스 워터리 오일', '겔랑 워터리오일', '페이셜오일', 1, '정제수, 글리세린, 꿀추출물, 로얄젤리추출물, 프로판디올', 'DEPT_STORE', 0),
    ('DEPT_005', '입생로랑', '퓨어 샷 나이트 리부트 세럼', '입생로랑 퓨어샷', '세럼/앰플', 1, '정제수, 글리콜산, 아르간커넬오일, 나이아신아마이드, 선인장꽃추출물', 'DEPT_STORE', 0),
    ('DEPT_006', '디올', '캡춰 토탈 르 세럼', '디올 캡춰토탈', '세럼/앰플', 1, '정제수, 글리세린, 론고자추출물, 소듐하이알루로네이트, 메도우폼씨오일', 'DEPT_STORE', 0),
    ('DEPT_007', '에스티로더', '리-뉴트리브 얼티미트 다이아몬드 크림', '에스티로더 다이아몬드', '크림', 1, '정제수, 송로버섯추출물, 스쿠알란, 진주가루, 글리세린', 'DEPT_STORE', 0)
]

conn = sqlite3.connect('e:/안티그래비티/cosmetic/database/cosmetic.db')
cursor = conn.cursor()
count = 0

for row in extra_data:
    id_val, brand, name, market_name, cat, is_luxury, ings_raw, source, is_kfda = row
    cursor.execute('''
        INSERT OR IGNORE INTO products 
        (id, brand_name, product_name, market_name, category, is_luxury, data_source, is_kfda_verified) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id_val, brand, name, market_name, cat, is_luxury, source, is_kfda))
    
    ingredients = [x.strip() for x in ings_raw.split(',')]
    for ing in ingredients:
        cursor.execute('INSERT OR IGNORE INTO ingredients (name_ko) VALUES (?)', (ing,))
        cursor.execute('SELECT id FROM ingredients WHERE name_ko = ?', (ing,))
        ing_id = cursor.fetchone()[0]
        cursor.execute('INSERT OR IGNORE INTO product_ingredients (product_id, ingredient_id) VALUES (?, ?)', (id_val, ing_id))
    
    count += 1

conn.commit()
print(f'Inserted {count} items from iHerb and Department stores.')
conn.close()
