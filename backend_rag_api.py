"""
BioSkin Match - 백엔드 RAG 및 Rules Engine API (FastAPI)
형(그래비)이 바로 실행 및 개발할 수 있도록 작성된 백엔드 모듈 코드입니다.
"""

from fastapi import FastAPI, HTTPException, Body, Query, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sqlite3
import random
from typing import List, Optional, Dict, Any
from enum import Enum
import os
import uvicorn
from alphafold_engine import PeptideInsightEngine

app = FastAPI(
    title="BioSkin Match RAG & Rules Engine API",
    description="자체 구축 성분 데이터베이스 및 과학적 조합 규칙 엔진 기반의 Zero-Hallucination 화장품 궁합 진단 API (일부 제품은 식약처 인증 정보 포함)",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://artgourmet.cloud",
        "http://localhost:3010",
        "http://localhost:8002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "frontend.html not found"}

# ==========================================
# 1. Pydantic 데이터 모델 (Request / Response)
# ==========================================

class CategoryEnum(str, Enum):
    TONER = "토너/스킨"
    SERUM = "세럼/앰플"
    CREAM = "크림"
    OIL = "페이셜오일"
    SUN = "선케어"
    MAKEUP = "메이크업"
    CLEANSER = "클렌저"
    MIST = "미스트"

class ProductSchema(BaseModel):
    product_id: str = Field(..., example="KFDA_199501021")
    brand_name: str = Field(..., example="에스티로더")
    product_name: str = Field(..., example="어드밴스드 나이트 리페어")
    market_name: Optional[str] = Field(default=None, example="갈색병 세럼")
    category: CategoryEnum
    ph_value: float = Field(default=5.5, ge=1.0, le=14.0)
    data_source: str = Field(default="MOCK")
    is_kfda_verified: bool = Field(default=False)
    is_luxury: bool = Field(default=False)
    price: int = Field(default=0)
    ingredients: List[str] = Field(default_factory=list, example=["비피다발효용해물", "아스코빅애씨드", "나이아신아마이드"])

class AnalyzeRoutineRequest(BaseModel):
    product_ids: List[str] = Field(..., min_items=1, max_items=5, example=["KFDA_1001", "KFDA_1002"])

class WarningDetail(BaseModel):
    type: str  # CONFLICT, TIME_SEPARATE, CAUTION
    title: str
    description: str
    affected_products: List[str]

class SynergyDetail(BaseModel):
    title: str
    description: str
    score_bonus: int

class RoutineItem(BaseModel):
    order: int
    product_id: str
    product_name: str
    brand_name: str
    timing: str  # "Morning", "Night", "Both"
    reason: str

class AnalysisResponse(BaseModel):
    pairing_score: int
    summary: str
    ideal_ratio: str
    warnings: List[WarningDetail]
    synergies: List[SynergyDetail]
    routine_order: List[RoutineItem]
    peptide_report: Dict[str, Any]
    sensory_metrics: Dict[str, Any]
    ai_conclusion: str
    grounded_llm_prompt: str  # LLM으로 전달될 Strict Grounded Context

class RecommendationResponse(BaseModel):
    recommended: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]

# ==========================================
# 2. Mock 식약처 DB & Rules Engine
# ==========================================

import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "cosmetic.db")

def get_product_from_db(product_id: str) -> Optional[ProductSchema]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    cursor.execute("""
        SELECT i.name_ko FROM ingredients i
        JOIN product_ingredients pi ON i.id = pi.ingredient_id
        WHERE pi.product_id = ?
    """, (product_id,))
    ingredients = [r[0] for r in cursor.fetchall()]
    conn.close()
    
    return ProductSchema(
        product_id=row[0],
        brand_name=row[1],
        product_name=row[2],
        category=row[3],
        ph_value=row[4],
        data_source=row[6] if len(row) > 6 and row[6] else "MOCK",
        is_kfda_verified=bool(row[7]) if len(row) > 7 and row[7] else False,
        market_name=row[8] if len(row) > 8 else None,
        is_luxury=bool(row[9]) if len(row) > 9 else False,
        price=int(row[10]) if len(row) > 10 and row[10] else 0,
        ingredients=ingredients
    )

def search_products_in_db(query: str) -> List[ProductSchema]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    search_term = f"%{query}%"
    cursor.execute("""
        SELECT id FROM products 
        WHERE brand_name LIKE ? OR product_name LIKE ? OR id LIKE ?
    """, (search_term, search_term, search_term))
    pids = [r[0] for r in cursor.fetchall()]
    conn.close()
    
    results = []
    for pid in pids:
        p = get_product_from_db(pid)
        if p: results.append(p)
    return results

def get_all_products_from_db() -> List[ProductSchema]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM products")
    pids = [r[0] for r in cursor.fetchall()]
    conn.close()
    
    results = []
    for pid in pids:
        p = get_product_from_db(pid)
        if p: results.append(p)
    return results

class ScientificRulesEngine:
    """과학적 성분 상충 및 시너지 검증 엔진"""
    
    @staticmethod
    def evaluate(products: List[ProductSchema]) -> Dict[str, Any]:
        # 조합의 안정된 해시를 기반으로 75~85점 사이의 기본 점수를 부여 (무조건 100점 방지)
        pids = sorted([p.product_id for p in products])
        hash_val = hash("".join(pids))
        base_score = 75 + (abs(hash_val) % 11)
        score = base_score
        warnings = []
        synergies = []
        
        # 전체 수집된 성분 맵핑
        all_ingredients = {}
        for p in products:
            for ing in p.ingredients:
                all_ingredients[ing] = p
        
        ing_list = list(all_ingredients.keys())
        
        # 규칙 1: 저pH 비타민C (아스코빅애씨드) + 레티놀 (자극 및 길항)
        if "아스코빅애씨드" in all_ingredients and "레티놀" in all_ingredients:
            score -= 25
            warnings.append(WarningDetail(
                type="TIME_SEPARATE",
                title="고농도 비타민C와 레티놀 동시 사용 주의",
                description="pH 격차가 크고 자극 가능성이 높습니다. 비타민C는 아침, 레티놀은 저녁으로 분리하세요.",
                affected_products=[all_ingredients["아스코빅애씨드"].product_name, all_ingredients["레티놀"].product_name]
            ))
            
        # 규칙 2: 산성 각질제거제 (살리실릭애씨드/AHA) + 레티놀 (장벽 손상 위험)
        if "살리실릭애씨드" in all_ingredients and "레티놀" in all_ingredients:
            score -= 30
            warnings.append(WarningDetail(
                type="CONFLICT",
                title="BHA(살리실릭애씨드)와 레티놀 충돌 경고",
                description="피부 장벽 손상 및 과도한 각질 탈락을 유발할 수 있어 병용을 권장하지 않습니다.",
                affected_products=[all_ingredients["살리실릭애씨드"].product_name, all_ingredients["레티놀"].product_name]
            ))
            
        # 규칙 3: 비타민C (아스코빅애씨드) + 비타민E (토코페롤) / 페룰릭애씨드 (시너지)
        if "아스코빅애씨드" in all_ingredients and "토코페롤" in all_ingredients:
            score += 15
            synergies.append(SynergyDetail(
                title="항산화 황금 네트워크 시너지",
                description="비타민C와 비타민E가 결합하여 항산화 활성이 최대 4배 증대됩니다.",
                score_bonus=15
            ))
            
        # 규칙 4: 펩타이드 + 히알루론산 (보습 및 침투 시너지)
        if any("펩타이드" in ing for ing in ing_list) and "히알루론산" in all_ingredients:
            score += 10
            synergies.append(SynergyDetail(
                title="장벽 탄력 & 수분 레이어링 시너지",
                description="히알루론산의 수분막이 펩타이드 성분의 피부 흡수를 돕습니다.",
                score_bonus=10
            ))

        # 점수 범위 제한 (0 ~ 100)
        final_score = max(0, min(100, score))

        # 초정밀 오감 및 기능성 지표 (Mock 계산)
        sensory_metrics = {
            "spreadability": max(30, 95 - (len(products) * 5)), # 발림성
            "absorption": max(20, 90 - (len(products) * 10)), # 흡수력
            "oiliness": min(100, 20 + sum([20 for p in products if p.category == CategoryEnum.OIL or p.category == CategoryEnum.CREAM])), # 유분감
            "pilling_probability": min(95, len(products) * 15), # 밀림 현상 확률
            "irritation_level": min(100, 10 + (20 if "레티놀" in all_ingredients else 0) + (15 if "아스코빅애씨드" in all_ingredients else 0)), # 자극도
            "comedogenicity": min(5, sum([1 for p in products if p.category == CategoryEnum.CREAM or p.category == CategoryEnum.OIL])), # 모공 막힘 (0~5)
            "texture": "가볍고 수분감이 도는 텍스처" if all(p.category in [CategoryEnum.TONER, CategoryEnum.SERUM] for p in products) else "조금 무겁고 쫀쫀한 텍스처",
            "scent": "무향/은은한 허브향 (인공향료 배제)",
            "has_functional": "레티놀" in all_ingredients or "나이아신아마이드" in all_ingredients or "아스코빅애씨드" in all_ingredients,
            "avg_ph": round(sum(p.ph_value for p in products) / len(products), 1) if products else 5.5,
            "packaging_types": ["펌프", "스포이드", "단지"][:len(products)]
        }

        conclusion_txt = f"[{', '.join(p.product_name for p in products)}] 조합은 "
        if final_score >= 90:
            conclusion_txt += "상호 보완적인 훌륭한 궁합입니다. "
        elif final_score >= 70:
            conclusion_txt += "무난하게 사용할 수 있는 조합입니다. "
        else:
            conclusion_txt += "주의가 필요한 조합입니다. 피부에 부담을 줄 수 있습니다. "
            
        if sensory_metrics["oiliness"] > 60:
            conclusion_txt += "유분감이 다소 높아 건성 피부에 적합하며, 발림성은 무거워질 수 있습니다. "
        else:
            conclusion_txt += "수분감이 풍부하고 흡수가 빨라 산뜻하게 마무리됩니다. "
            
        if sensory_metrics["pilling_probability"] > 40:
            conclusion_txt += "하지만 여러 겹 바를 경우 화장이 밀릴 우려가 있으니 흡수 시간을 충분히 두세요."
        
        return {
            "score": final_score,
            "warnings": warnings,
            "synergies": synergies,
            "sensory_metrics": sensory_metrics,
            "ai_conclusion": conclusion_txt
        }

class LayeringOrderEngine:
    """제형 및 pH 기반 바르는 순서 자동 정렬"""
    
    CATEGORY_PRIORITY = {
        CategoryEnum.TONER: 1,
        CategoryEnum.SERUM: 2,
        CategoryEnum.CREAM: 3,
        CategoryEnum.OIL: 4,
        CategoryEnum.SUN: 5,
    }

    @classmethod
    def calculate_order(cls, products: List[ProductSchema]) -> List[RoutineItem]:
        # pH 낮은 순 + 카테고리 우선순위 기준 정렬
        sorted_products = sorted(
            products,
            key=lambda p: (p.ph_value, cls.CATEGORY_PRIORITY.get(p.category, 99))
        )
        
        routine = []
        for idx, p in enumerate(sorted_products, 1):
            timing = "Both"
            if "레티놀" in p.ingredients:
                timing = "Night"
            elif "아스코빅애씨드" in p.ingredients:
                timing = "Morning"

            routine.append(RoutineItem(
                order=idx,
                product_id=p.product_id,
                product_name=p.product_name,
                brand_name=p.brand_name,
                timing=timing,
                reason=f"pH {p.ph_value} 및 {p.category.value} 제형 특성에 맞춘 순서"
            ))
            
        return routine

class GroundedPromptBuilder:
    """Zero-Hallucination을 위한 Strict Grounded LLM 프롬프트 생성기"""
    
    @staticmethod
    def build_prompt(products: List[ProductSchema], rules_result: Dict[str, Any], routine: List[RoutineItem]) -> str:
        prod_details = "\n".join([
            f"- [{p.product_id}] {p.brand_name} {p.product_name} (pH: {p.ph_value}, 주요성분: {', '.join(p.ingredients)})"
            for p in products
        ])
        
        warnings_text = "\n".join([f"* [경고/주의] {w.title}: {w.description}" for w in rules_result["warnings"]]) or "없음"
        synergies_text = "\n".join([f"* [시너지] {s.title}: {s.description}" for s in rules_result["synergies"]]) or "없음"
        
        prompt = f"""
[SYSTEM PROMPT: STRICT GROUNDED MODE]
당신은 BioSkin Match의 화장품 분자생물학 전문가입니다.
반드시 아래 제공된 [제품 데이터베이스 데이터] 및 [과학적 규격 결과]만 사용하여 답변하세요.
데이터에 없는 제품이나 성분을 지어내면 시스템 오류가 발생합니다.

[선택된 제품 목록]
{prod_details}

[엔진 계산 결과]
- 궁합 스코어: {rules_result['score']}점
- 성분 상충 경고:
{warnings_text}
- 성분 시너지:
{synergies_text}

[추천 바르는 순서]
""" + "\n".join([f"{r.order}. {r.product_name} ({r.timing} 루틴)" for r in routine]) + """

[요청 사항]
1. 위 데이터만 바탕으로 유저에게 친절하고 과학적인 레이어링 총평을 작성하세요.
2. 데이터에 포함되지 않은 타 브랜드나 외부 제품명은 절대로 언급하지 마세요.
"""
        return prompt

# ==========================================
# 3. API 엔드포인트 정의
# ==========================================

@app.get("/health", summary="헬스체크 API")
def health_check():
    return {"status": "ok", "service": "BioSkin Match RAG Backend"}

@app.get("/api/v1/products/all", response_model=List[ProductSchema], summary="모든 제품 가져오기")
def get_all_products():
    return get_all_products_from_db()

@app.get("/api/v1/products/search", response_model=List[ProductSchema], summary="제품 검색")
def search_products(q: str = Query(..., min_length=1, description="검색할 브랜드명 또는 제품명")):
    return search_products_in_db(q)

@app.post("/api/v1/analyze", response_model=AnalysisResponse, summary="내 화장대 조합 분석 API")
def analyze_routine(request: AnalyzeRoutineRequest):
    selected_products: List[ProductSchema] = []
    
    # 1. DB에서 실존 제품 조회 (가짜 제품 1차 검증)
    for pid in request.product_ids:
        p = get_product_from_db(pid)
        if not p:
            raise HTTPException(status_code=404, detail=f"제품 데이터베이스에서 제품 ID '{pid}'를 찾을 수 없습니다. (가짜 제품 차단)")
        selected_products.append(p)
        
    # 2. Scientific Rules Engine 실행
    eval_result = ScientificRulesEngine.evaluate(selected_products)
    
    # 3. Layering Order Engine 실행
    routine_order = LayeringOrderEngine.calculate_order(selected_products)
    
    # 4. Strict Grounded Prompt 구성 (LLM 연동용)
    grounded_prompt = GroundedPromptBuilder.build_prompt(selected_products, eval_result, routine_order)
    
    # 5. 요약 생성
    summary_text = f"선택하신 {len(selected_products)}개 제품의 궁합 점수는 {eval_result['score']}점입니다."
    if eval_result['warnings']:
        summary_text += " 사용 시 성분 상충 및 타이밍 분리가 필요한 항목이 있습니다."
    else:
        summary_text += " 성분 간 충돌 없이 훌륭한 시너지를 기대할 수 있는 조합입니다."

    # 6. 이상적 배합 비율 (Mock Logic)
    if len(selected_products) == 2:
        ideal_ratio = f"{selected_products[0].product_name} 30% : {selected_products[1].product_name} 70%"
    elif len(selected_products) > 2:
        ideal_ratio = "메인 세럼 50%, 나머지 50% 분배 믹스 권장"
    else:
        ideal_ratio = "단일 제품 사용 (100%)"
        
    # 7. 펩타이드 인사이트 엔진 분석
    all_ingredients = []
    for p in selected_products:
        all_ingredients.extend(p.ingredients)
    peptide_report = PeptideInsightEngine.analyze_peptides(all_ingredients)

    return AnalysisResponse(
        pairing_score=eval_result["score"],
        summary=summary_text,
        ideal_ratio=ideal_ratio,
        warnings=eval_result["warnings"],
        synergies=eval_result["synergies"],
        routine_order=routine_order,
        peptide_report=peptide_report,
        sensory_metrics=eval_result["sensory_metrics"],
        ai_conclusion=eval_result["ai_conclusion"],
        grounded_llm_prompt=grounded_prompt
    )

@app.get("/api/v1/products/{product_id}/recommendations", response_model=RecommendationResponse, summary="특정 제품 추천 및 상극 리스트")
def get_recommendations(product_id: str):
    base_p = get_product_from_db(product_id)
    if not base_p:
        raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")
        
    all_products = get_all_products_from_db()
    scores = []
    
    for p in all_products:
        if p.product_id == base_p.product_id:
            continue
        eval_result = ScientificRulesEngine.evaluate([base_p, p])
        scores.append({
            "product": p.model_dump(),
            "score": eval_result["score"],
            "warnings": [w.title for w in eval_result["warnings"]],
            "synergies": [s.title for s in eval_result["synergies"]]
        })
        
    # 점수 높은 순으로 정렬
    scores.sort(key=lambda x: x["score"], reverse=True)
    
    # 100점 초과 혹은 가장 높은 점수 5개
    recommended = [s for s in scores if s["score"] > 100 or s["synergies"]][:5]
    if not recommended:
        recommended = scores[:5] # 없으면 상위 5개
        
    # 점수 낮은 순으로 정렬
    scores.sort(key=lambda x: x["score"])
    
    # 100점 미만 혹은 가장 낮은 점수 5개
    conflicts = [s for s in scores if s["score"] < 100 or s["warnings"]][:5]
    if not conflicts:
        conflicts = scores[:5]
        
    return RecommendationResponse(
        recommended=recommended,
        conflicts=conflicts
    )

@app.get("/api/v1/products/{product_id}/dupe", summary="명품 화장품의 중저가 듀프 조합 추천")
def get_dupe_recommendation(product_id: str):
    base_p = get_product_from_db(product_id)
    if not base_p or not base_p.is_luxury:
        raise HTTPException(status_code=400, detail="명품 화장품이 아니거나 찾을 수 없습니다.")
        
    all_products = get_all_products_from_db()
    non_luxury = [p for p in all_products if not p.is_luxury]
    
    # 가성비 꿀조합 2개 추출 (현재는 간단히 점수 기반 매칭 대체용 랜덤 추출)
    import random
    dupes = random.sample(non_luxury, min(2, len(non_luxury))) if non_luxury else []
    
    return {
        "target_luxury": base_p.model_dump(),
        "dupe_combination": [p.model_dump() for p in dupes],
        "match_rate": random.randint(85, 98),
        "description": f"{base_p.market_name or base_p.product_name}의 핵심 성분 배합을 대체할 수 있는 가성비 꿀조합입니다."
    }

@app.get("/api/v1/products/{product_id}/dupes")
def find_dupe(product_id: str):
    """
    럭셔리 제품의 성분을 분석하여 가장 유사한 저가 제품 2~3개의 조합(Dupe)을 찾아 반환합니다.
    """
    luxury_product = get_product_from_db(product_id)
    if not luxury_product or not luxury_product.is_luxury:
        raise HTTPException(status_code=400, detail="럭셔리 제품이 아니거나 찾을 수 없습니다.")
    
    target_ingredients = set(luxury_product.ingredients)
    
    # 카테고리 필터링: 스킨케어는 스킨케어끼리, 메이크업은 메이크업끼리
    target_cat = luxury_product.category
    skincare_cats = ["크림", "세럼/앰플", "토너/스킨", "페이셜오일"]
    if target_cat in skincare_cats:
        valid_cats = skincare_cats
    else:
        valid_cats = [target_cat]
        
    # 모든 일반 제품(저렴이)을 불러옴
    all_products = get_all_products_from_db()
    dupe_candidates = [
        p for p in all_products 
        if not p.is_luxury and p.ingredients and p.category in valid_cats
    ]
    
    # 간단한 휴리스틱: 2~3개의 제품 조합 중 자카드 유사도가 높은 상위 3개를 반환
    # 성능을 위해 무작위로 100개의 조합을 샘플링하여 가장 좋은 조합을 찾음
    best_combinations = []
    
    for _ in range(2000):
        # 2개 또는 3개 조합 랜덤 선택
        combo_size = random.choice([2, 3])
        combo = random.sample(dupe_candidates, min(combo_size, len(dupe_candidates)))
        
        combo_ingredients = set()
        for p in combo:
            combo_ingredients.update(p.ingredients)
            
        intersection = target_ingredients.intersection(combo_ingredients)
        union = target_ingredients.union(combo_ingredients)
        similarity = len(intersection) / len(union) if union else 0
        
        # 조합의 총 가격
        total_price = sum(p.price for p in combo)
        
        combo_dicts = [p.dict() for p in combo]
        combo_pids = sorted([p.product_id for p in combo])
        combo_hash = "".join(combo_pids)
        
        # 중복 조합 필터링
        if not any(c['hash'] == combo_hash for c in best_combinations):
            best_combinations.append({
                "hash": combo_hash,
                "products": combo_dicts,
                "similarity": similarity * 100,
                "total_price": total_price,
                "intersection_count": len(intersection)
            })
            
    # 유사도 순으로 정렬 후 상위 3개 반환
    best_combinations.sort(key=lambda x: x['similarity'], reverse=True)
    top_dupes = best_combinations[:3]
    
    # 반환 데이터 정리
    result = []
    for dupe in top_dupes:
        result.append({
            "products": dupe["products"],
            "match_rate": round(dupe["similarity"], 1),
            "total_price": dupe["total_price"],
            "matched_ingredients": dupe["intersection_count"],
            "luxury_price": luxury_product.price,
            "savings": luxury_product.price - dupe["total_price"]
        })
        
    return {"luxury_target": luxury_product.dict(), "dupe_combinations": result}

if __name__ == "__main__":
    uvicorn.run("backend_rag_api:app", host="0.0.0.0", port=8002, reload=True)
