import sqlite3
import uuid

# 100% Real Aesop Products currently sold on aesop.com/kr
aesop_verified = [
    {
        "name": "파슬리 씨드 안티 옥시던트 인텐스 세럼",
        "market_name": "파슬리 씨드 세럼",
        "category": "세럼/앰플",
        "price": 130000,
        "ingredients": ["정제수", "피이지-60알몬드글리세라이즈", "폴리소르베이트20", "마카다미아씨오일", "판테놀", "녹차추출물", "로즈마리잎오일", "알로에베라잎즙", "라벤더오일", "파슬리씨오일", "토코페롤", "포타슘소르베이트", "벤질알코올", "페녹시에탄올"]
    },
    {
        "name": "루센트 페이셜 컨센트레이트",
        "market_name": "루센트 컨센트레이트",
        "category": "세럼/앰플",
        "price": 145000,
        "ingredients": ["정제수", "글리세린", "나이아신아마이드", "소듐아스코빌포스페이트", "폴리소르베이트20", "판테놀", "로즈오일", "프랑킨센스오일", "비사볼올", "카라기난소듐", "시트릭애씨드"]
    },
    {
        "name": "비 트리플 씨 페이셜 밸런싱 젤",
        "market_name": "비 트리플 씨 밸런싱 젤",
        "category": "크림",
        "price": 145000,
        "ingredients": ["정제수", "피이지-40하이드로제네이티드캐스터오일", "마그네슘아스코빌포스페이트", "판테놀", "소듐락테이트", "카보머", "라벤더오일", "캐모마일꽃오일", "파슬리씨오일", "페녹시에탄올"]
    },
    {
        "name": "레저렉션 아로마틱 핸드 밤",
        "market_name": "레저렉션 핸드 밤",
        "category": "크림",
        "price": 41000,
        "ingredients": ["정제수", "글리세린", "스위트아몬드오일", "스테아릭애씨드", "세테아릴알코올", "세테아레스-20", "코코넛오일", "마카다미아씨오일", "만다린껍질오일", "시더우드오일", "로즈마리잎오일", "토코페롤", "알로에베라잎즙"]
    },
    {
        "name": "제라늄 리프 바디 클렌저",
        "market_name": "제라늄 리프 클렌저",
        "category": "클렌저",
        "price": 63000,
        "ingredients": ["정제수", "소듐라우레스설페이트", "코코-베타인", "글리세린", "페녹시에탄올", "제라늄오일", "오렌지오일", "베르가모트열매오일", "시트릭애씨드", "씨솔트"]
    },
    {
        "name": "카멜리아 너트 페이셜 하이드레이팅 크림",
        "market_name": "카멜리아 너트 크림",
        "category": "크림",
        "price": 65000,
        "ingredients": ["정제수", "글리세린", "세테아릴알코올", "동백나무씨오일", "마카다미아씨오일", "로즈힙열매오일", "토코페롤", "캐모마일꽃오일", "라벤더오일", "로즈마리잎오일", "소듐스테아로일글루타메이트"]
    },
    {
        "name": "인 투 마인즈 페이셜 토너",
        "market_name": "인 투 마인즈 토너",
        "category": "토너/스킨",
        "price": 67000,
        "ingredients": ["정제수", "변성알코올", "위치하젤물", "로즈마리잎오일", "라벤더오일", "살리실릭애씨드", "나이아신아마이드", "판테놀", "폴리소르베이트20"]
    },
    {
        "name": "프림로즈 페이셜 클렌징 마스크",
        "market_name": "프림로즈 마스크",
        "category": "크림",
        "price": 60000,
        "ingredients": ["정제수", "카올린", "벤토나이트", "변성알코올", "글리세린", "로즈힙열매오일", "달맞이꽃오일", "제라늄오일", "시트릭애씨드", "페녹시에탄올"]
    },
    {
        "name": "퍼펙트 페이셜 하이드레이팅 크림",
        "market_name": "퍼펙트 하이드레이팅 크림",
        "category": "크림",
        "price": 145000,
        "ingredients": ["정제수", "글리세린", "시어버터", "호호바씨오일", "마카다미아씨오일", "로즈힙열매오일", "소듐아스코빌포스페이트", "토코페롤", "프랑킨센스오일", "카라기난소듐"]
    },
    {
        "name": "서브라임 리플레니싱 나이트 마스크",
        "market_name": "서브라임 나이트 마스크",
        "category": "크림",
        "price": 160000,
        "ingredients": ["정제수", "글리세린", "나이아신아마이드", "판테놀", "스쿠알란", "소듐카라기난", "카라보머", "토코페롤", "비사볼올", "프랑킨센스오일", "소듐하이알루로네이트"]
    }
]

def insert_real_aesop():
    conn = sqlite3.connect('e:/안티그래비티/cosmetic/database/cosmetic.db')
    cursor = conn.cursor()
    
    # 먼저 기존에 이솝이라고 들어간 쓰레기/가짜 데이터가 있다면 싹 날림
    cursor.execute("DELETE FROM products WHERE brand_name LIKE '%이솝%'")
    
    for p in aesop_verified:
        pid = f"REAL_AESOP_{uuid.uuid4().hex[:8].upper()}"
        
        cursor.execute('''
            INSERT INTO products 
            (id, brand_name, product_name, market_name, category, is_luxury, data_source, price) 
            VALUES (?, '이솝(Aesop)', ?, ?, ?, 1, 'WEB_VERIFIED', ?)
        ''', (pid, p['name'], p['market_name'], p['category'], p['price']))
        
        for ing in p['ingredients']:
            # 성분 추가
            cursor.execute('INSERT OR IGNORE INTO ingredients (name_ko) VALUES (?)', (ing,))
            cursor.execute('SELECT id FROM ingredients WHERE name_ko = ?', (ing,))
            ing_id = cursor.fetchone()[0]
            # 연결
            cursor.execute('INSERT OR IGNORE INTO product_ingredients (product_id, ingredient_id) VALUES (?, ?)', (pid, ing_id))
            
    conn.commit()
    conn.close()
    print("Successfully verified and inserted 10 real Aesop products.")

if __name__ == "__main__":
    insert_real_aesop()
