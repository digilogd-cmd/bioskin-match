-- 화장품 제품 정보 테이블
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,           -- 고유 ID (예: OY_12345)
    brand_name TEXT NOT NULL,      -- 브랜드명
    product_name TEXT NOT NULL,    -- 제품명
    category TEXT NOT NULL,        -- 카테고리 (토너/스킨, 세럼/앰플, 크림, 선케어 등)
    ph_value REAL DEFAULT 5.5,     -- pH 값 (기본 5.5)
    image_url TEXT,                -- 상품 이미지 URL
    data_source TEXT DEFAULT 'MOCK', -- 데이터 출처 (MOCK, OLIVEYOUNG, HWAHAE)
    is_kfda_verified INTEGER DEFAULT 0 -- 식약처 API 팩트체크 완료 여부 (0:미인증, 1:인증)
);

-- 성분 사전 테이블
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ko TEXT NOT NULL UNIQUE,  -- 성분 한글명
    name_en TEXT,                  -- 성분 영문명
    description TEXT,              -- 성분 설명 및 효능
    ewg_score TEXT                 -- EWG 스코어 (예: "1-2")
);

-- 제품-성분 N:M 매핑 테이블
CREATE TABLE IF NOT EXISTS product_ingredients (
    product_id TEXT NOT NULL,
    ingredient_id INTEGER NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY(ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    PRIMARY KEY(product_id, ingredient_id)
);
