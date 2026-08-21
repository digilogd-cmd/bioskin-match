import sqlite3
import json
import os
import re

DB_PATH = "e:/안티그래비티/cosmetic/database/cosmetic.db"
SCHEMA_PATH = "e:/안티그래비티/cosmetic/database/schema.sql"

REAL_DATA_SEED = [
    {
        "id": "OY_1001",
        "brand": "에스티로더",
        "name": "어드밴스드 나이트 리페어 (갈색병)",
        "category": "세럼/앰플",
        "ph_value": 5.0,
        "ingredients": "정제수, 비피다발효용해물, 피이지-8, 프로판다이올, 비스-피이지-18메틸에터다이메틸실레인, 메틸글루세스-20, 글리세레스-26, 피이지-75, 부틸렌글라이콜, 바오밥나무씨추출물, 트라이펩타이드-32, 소듐하이알루로네이트, 효모추출물, 락토바실러스발효물, 콜라씨추출물, 캐모마일꽃추출물, 스쿠알란, 아데노신"
    },
    {
        "id": "OY_1002",
        "brand": "스킨슈티컬즈",
        "name": "C E 페룰릭 안티옥시던트 세럼",
        "category": "세럼/앰플",
        "ph_value": 3.0,
        "ingredients": "정제수, 에톡시다이글라이콜, 아스코빅애씨드(15%), 글리세린, 프로필렌글라이콜, 라우레스-23, 페녹시에탄올, 토코페롤(1%), 트라이에탄올아민, 페룰릭애씨드(0.5%), 판테놀, 소듐하이알루로네이트"
    },
    {
        "id": "OY_1003",
        "brand": "폴라초이스",
        "name": "스킨 퍼펙팅 2% BHA 리퀴드",
        "category": "토너/스킨",
        "ph_value": 3.5,
        "ingredients": "정제수, 메틸프로판다이올, 부틸렌글라이콜, 살리실릭애씨드(2%), 녹차추출물, 폴리솔베이트20, 소듐하이드록사이드, 테트라소듐이디티에이"
    },
    {
        "id": "OY_1004",
        "brand": "디오디너리",
        "name": "레티놀 0.5% 인 스쿠알란",
        "category": "세럼/앰플",
        "ph_value": 6.0,
        "ingredients": "스쿠알란, 카프릴릭/카프릭트라이글리세라이드, 레티놀, 솔비탄올리에이트, 호호바씨오일, 토마토추출물, 로즈마리잎추출물, 옥틸도데칸올, 비에이치티"
    },
    {
        "id": "OY_1005",
        "brand": "토리든",
        "name": "다이브인 저분자 히알루론산 세럼",
        "category": "세럼/앰플",
        "ph_value": 5.5,
        "ingredients": "정제수, 부틸렌글라이콜, 글리세린, 다이프로필렌글라이콜, 1,2-헥산다이올, 판테놀, 소듐하이알루로네이트, 하이드롤라이즈드하이알루로닉애씨드, 소듐아세틸레이티드하이알루로네이트, 소듐하이알루로네이트크로스폴리머, 하이드롤라이즈드소듐하이알루로네이트, 알란토인, 마카다미아씨오일, 세라마이드엔피, 알에이치-올리고펩타이드-1"
    }
]

def create_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema = f.read()
    conn.executescript(schema)
    return conn

def clean_ingredient_name(name):
    # 퍼센트 제거나 불필요한 공백 제거
    name = re.sub(r'\(.*?\)', '', name)
    return name.strip()

def build_db(conn):
    cursor = conn.cursor()
    
    ingredient_map = {} # name -> id
    
    for product in REAL_DATA_SEED:
        # 1. 상품 등록
        cursor.execute(
            "INSERT INTO products (id, brand_name, product_name, category, ph_value) VALUES (?, ?, ?, ?, ?)",
            (product["id"], product["brand"], product["name"], product["category"], product["ph_value"])
        )
        
        # 2. 성분 분리 및 등록
        ingredients_raw = product["ingredients"].split(',')
        for ing_raw in ingredients_raw:
            ing_clean = clean_ingredient_name(ing_raw)
            if not ing_clean: continue
            
            if ing_clean not in ingredient_map:
                cursor.execute(
                    "INSERT INTO ingredients (name_ko) VALUES (?)",
                    (ing_clean,)
                )
                ingredient_map[ing_clean] = cursor.lastrowid
                
            ing_id = ingredient_map[ing_clean]
            
            # 3. 매핑
            try:
                cursor.execute(
                    "INSERT INTO product_ingredients (product_id, ingredient_id) VALUES (?, ?)",
                    (product["id"], ing_id)
                )
            except sqlite3.IntegrityError:
                pass # 중복 매핑 무시
                
    conn.commit()
    
    # 확인 쿼리
    cursor.execute("SELECT count(*) FROM products")
    print(f"Products created: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT count(*) FROM ingredients")
    print(f"Ingredients extracted: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT count(*) FROM product_ingredients")
    print(f"Mappings created: {cursor.fetchone()[0]}")

if __name__ == "__main__":
    conn = create_db()
    build_db(conn)
    conn.close()
    print("Database build complete!")
