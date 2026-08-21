import requests
import json
import os
import urllib.parse
from typing import Dict, Any


def _load_dotenv(path: str = ".env") -> None:
    """의존성 추가 없이 .env 파일을 os.environ에 로드 (이미 설정된 값은 덮어쓰지 않음)"""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


class KfdaApiClient:
    def __init__(self):
        # 식약처 공공데이터포털 API 인증키 - .env 파일의 KFDA_API_KEY로 주입 (저장소에 커밋되지 않음)
        self.api_key = os.environ.get("KFDA_API_KEY", "")
        if not self.api_key:
            raise RuntimeError("KFDA_API_KEY가 설정되지 않았습니다. .env 파일을 만들고 KFDA_API_KEY=... 를 채워주세요 (.env.example 참고).")
        self.base_url = "https://apis.data.go.kr/1471000/CsmtcsUseRstrcInfoService/getCsmtcsUseRstrcInfoList"

    def get_restricted_ingredients(self, ingredient_name: str = "", page_no: int = 1, num_of_rows: int = 10) -> Dict[str, Any]:
        """
        화장품 사용제한 원료정보를 식약처 API에서 조회합니다.
        """
        # API URL 구성 (인증키가 이미 인코딩되어 있으므로 파라미터를 수동 조합하거나 디코딩해서 넘겨야 할 수 있음)
        # requests의 params로 넘길 때는 Decoding 된 키를 넘겨야 2번 인코딩되지 않음
        decoded_key = urllib.parse.unquote(self.api_key)
        
        params = {
            "ServiceKey": decoded_key,
            "pageNo": str(page_no),
            "numOfRows": str(num_of_rows),
            "type": "json"
        }
        
        if ingredient_name:
            params["ingr_kor_name"] = ingredient_name
            
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    print("JSON 파싱 에러. 응답 내용:", response.text)
                    return {"error": "Invalid JSON response"}
            else:
                print(f"API 요청 실패: {response.status_code}")
                return {"error": f"HTTP Error {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    client = KfdaApiClient()
    print("식약처 API 연결 테스트 중...")
    result = client.get_restricted_ingredients(num_of_rows=3)
    print(json.dumps(result, indent=2, ensure_ascii=False))
