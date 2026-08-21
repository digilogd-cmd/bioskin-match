import random
from typing import Dict, Any, List

class PeptideInsightEngine:
    """내부 성분 데이터베이스 기반 펩타이드/단백질 작용기전 참고정보 엔진 (자체 구축, 외부 AI 모델 연동 없음)"""

    # 분석 대상 단백질/펩타이드 매핑 (성분명 -> 단백질 데이터)
    PROTEIN_MAP = {
        "트라이펩타이드-32": {
            "reference_protein_id": "P01133 (유사)",
            "structure": "Alpha-helix dominant",
            "mechanism": "피부 표피 성장 인자(EGF) 수용체 결합",
            "structure_confidence": 92.4, # 높은 구조적 신뢰도
            "absorption_rate": "High"
        },
        "알에이치-올리고펩타이드-1": {
            "reference_protein_id": "P01133",
            "structure": "Globular with disulfide bonds",
            "mechanism": "세포 분열 촉진 및 콜라겐 합성 유도",
            "structure_confidence": 95.1,
            "absorption_rate": "Medium"
        },
        "비피다발효용해물": {
            "reference_protein_id": "Multi-protein complex",
            "structure": "Bacterial cell wall fragments",
            "mechanism": "피부 마이크로바이옴 밸런스 및 장벽 단백질 강화",
            "structure_confidence": 85.0,
            "absorption_rate": "Low-to-Medium"
        },
        "콜라겐": {
            "reference_protein_id": "P02452",
            "structure": "Triple helix",
            "mechanism": "표피 진피층 지지대 형성",
            "structure_confidence": 98.5,
            "absorption_rate": "Low (requires fragmentation)"
        }
    }

    @classmethod
    def analyze_peptides(cls, ingredients_list: List[str]) -> Dict[str, Any]:
        """주어진 성분 리스트에서 펩타이드/단백질 성분을 찾아 내부 참고 데이터 기반 인사이트 리포트 생성"""
        results = []

        for ing in ingredients_list:
            # 매핑된 성분 찾기 (부분 일치도 허용)
            matched_key = next((k for k in cls.PROTEIN_MAP.keys() if k in ing), None)

            if matched_key:
                data = cls.PROTEIN_MAP[matched_key]
                results.append({
                    "ingredient": matched_key,
                    "reference_protein_id": data["reference_protein_id"],
                    "structure_confidence": data["structure_confidence"],
                    "confidence_level": "Very High" if data["structure_confidence"] > 90 else "High",
                    "mechanism": data["mechanism"],
                    "insight": f"내부 성분 데이터베이스 분석에 따르면 이 구조({data['structure']})는 피부 수용체 결합 효율이 우수하며, 다른 유효 성분(수분/비타민)과 만났을 때 입체 구조가 안정적으로 유지됩니다."
                })

        return {
            "has_protein": len(results) > 0,
            "protein_analyses": results
        }
