import sqlite3
import random
import uuid

DB_PATH = "e:/안티그래비티/cosmetic/database/cosmetic.db"

brands = ["에스티로더", "랑콤", "설화수", "헤라", "이니스프리", "닥터지", "라운드랩", "토리든", "메디힐", "아비브", "구달", "마녀공장", "아이소이", "코스알엑스", "디오디너리", "라로슈포제", "키엘", "크리니크", "피지오겔", "바이오더마"]
categories = ["토너/스킨", "세럼/앰플", "크림", "페이셜오일", "선케어"]
product_keywords = {
    "토너/스킨": ["토너", "스킨", "에센스 워터", "부스팅 토너", "패드", "토닝 로션"],
    "세럼/앰플": ["세럼", "앰플", "컨센트레이트", "에센스", "리페어 세럼", "블레미쉬 앰플"],
    "크림": ["크림", "수분크림", "배리어 크림", "안티에이징 크림", "시카 크림", "리페어 크림"],
    "페이셜오일": ["오일", "페이스 오일", "트리트먼트 오일", "리커버리 오일"],
    "선케어": ["선크림", "선스크린", "선스틱", "무기자차", "유기자차", "UV 디펜스"]
}

ingredients_pool = [
    "정제수", "글리세린", "부틸렌글라이콜", "나이아신아마이드", "판테놀", "알란토인", "소듐하이알루로네이트", "히알루론산", 
    "병풀추출물", "마데카소사이드", "아시아티코사이드", "어성초추출물", "티트리잎오일", "알로에베라잎즙", "녹차추출물", 
    "아스코빅애씨드", "비타민C", "토코페롤", "비타민E", "레티놀", "레티닐팔미테이트", "바쿠치올", 
    "살리실릭애씨드", "BHA", "글라이콜릭애씨드", "AHA", "락틱애씨드", "PHA", 
    "세라마이드엔피", "콜레스테롤", "피토스핑고신", "스쿠알란", "호호바씨오일", "해바라기씨오일", "시어버터", 
    "트라이펩타이드-32", "알에이치-올리고펩타이드-1", "아세틸헥사펩타이드-8", "카퍼트라이펩타이드-1", "비피다발효용해물", "갈락토미세스발효여과물", "콜라겐추출물", 
    "아데노신", "알부틴", "트라넥사믹애씨드", "글루타티온",
    "다이메티콘", "사이클로펜타실록세인", "징크옥사이드", "티타늄디옥사이드", "에칠헥실메톡시신나메이트"
]

def generate_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 성분 풀 등록
    cursor.execute("DELETE FROM ingredients")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM product_ingredients")
    
    ingredient_ids = {}
    for ing in ingredients_pool:
        cursor.execute("INSERT INTO ingredients (name_ko) VALUES (?)", (ing,))
        ingredient_ids[ing] = cursor.lastrowid
        
    # 2. 500개의 제품 생성
    for i in range(1, 501):
        pid = f"KFDA_{20000000 + i}"
        brand = random.choice(brands)
        cat = random.choice(categories)
        keyword = random.choice(product_keywords[cat])
        
        # 제품명 생성 (예: 병풀 수분 크림, 비타민 리페어 세럼)
        prefix = random.choice(["", "딥 모이스처 ", "퓨어 ", "센서티브 ", "인텐시브 ", "퍼펙트 ", "어드밴스드 ", "리얼 ", "마일드 "])
        feature = random.choice(["수분 ", "진정 ", "미백 ", "탄력 ", "시카 ", "콜라겐 ", "장벽 ", "포어 "])
        name = f"{prefix}{feature}{keyword}"
        
        # pH 값 (산성~알칼리성 카테고리별 다름)
        if cat == "토너/스킨": ph = round(random.uniform(4.5, 6.5), 1)
        elif cat == "세럼/앰플": ph = round(random.uniform(3.5, 6.0), 1)
        else: ph = round(random.uniform(5.0, 7.0), 1)
        
        cursor.execute("""
            INSERT INTO products (id, brand_name, product_name, category, ph_value)
            VALUES (?, ?, ?, ?, ?)
        """, (pid, brand, name, cat, ph))
        
        # 3. 성분 매핑 (5~15개 랜덤)
        num_ing = random.randint(5, 15)
        # 특정 확률로 유효 성분 주입 (레티놀, 비타민C, 펩타이드 등)
        selected_ings = set(["정제수", "글리세린"])
        
        if "미백" in name or "비타민" in name: selected_ings.update(["아스코빅애씨드", "나이아신아마이드"])
        if "진정" in name or "시카" in name: selected_ings.update(["병풀추출물", "마데카소사이드", "판테놀"])
        if "탄력" in name or "어드밴스드" in name: selected_ings.update(["레티놀", "아데노신", "트라이펩타이드-32", "비피다발효용해물"])
        if "장벽" in name: selected_ings.update(["세라마이드엔피", "콜레스테롤"])
        if cat == "선케어": selected_ings.update(["징크옥사이드", "티타늄디옥사이드"])
        
        # 나머지 랜덤 채우기
        while len(selected_ings) < num_ing:
            selected_ings.add(random.choice(ingredients_pool))
            
        for ing in selected_ings:
            cursor.execute("""
                INSERT INTO product_ingredients (product_id, ingredient_id)
                VALUES (?, ?)
            """, (pid, ingredient_ids[ing]))
            
    conn.commit()
    conn.close()
    print(f"✅ 화장품 500개 대용량 데이터 생성 및 DB 주입 완료!")

if __name__ == '__main__':
    generate_db()
