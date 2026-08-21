import asyncio
from playwright.async_api import async_playwright
import json
import re

class OliveYoungScraper:
    def __init__(self):
        self.base_url = "https://www.oliveyoung.co.kr"

    async def init_browser(self):
        self.playwright = await async_playwright().start()
        # Headless 모드로 띄우되, 차단 방지를 위해 일반 유저인 것처럼 헤더/브라우저 위장
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()

    async def close(self):
        await self.browser.close()
        await self.playwright.stop()

    async def get_product_list(self, category_id, limit=20):
        """특정 카테고리의 상품 목록 및 goodsNo 추출"""
        url = f"{self.base_url}/store/display/getMCategoryList.do?dispCatNo={category_id}&fltDispCatNo=&prdSort=01&pageIdx=1&rowsPerPage={limit}"
        
        try:
            await self.page.goto(url, wait_until="networkidle")
        except Exception as e:
            print("네트워크 로딩 에러:", e)
            return []

        products = []
        # 상품 리스트 엘리먼트들 찾기
        items = await self.page.query_selector_all('.prd_info')
        for item in items:
            try:
                a_tag = await item.query_selector('a')
                if not a_tag: continue
                
                # onclick 속성에서 goodsNo 추출
                onclick_attr = await a_tag.get_attribute('onclick')
                match = re.search(r"goodsDetail\('([A-Z0-9]+)'", onclick_attr or "")
                if not match: continue
                
                goods_no = match.group(1)
                
                brand_elem = await item.query_selector('.tx_brand')
                brand = await brand_elem.inner_text() if brand_elem else "Unknown"
                brand = brand.strip()
                
                name_elem = await item.query_selector('.tx_name')
                name = await name_elem.inner_text() if name_elem else "Unknown"
                name = name.strip()
                
                products.append({
                    "id": f"OY_{goods_no}",
                    "brand": brand,
                    "name": name,
                    "goodsNo": goods_no
                })
            except Exception as e:
                pass
                
        return products

    async def get_product_ingredients(self, goods_no):
        """특정 상품의 전성분 정보 텍스트 추출"""
        # AJAX 통신 URL을 직접 쳐서 가져오는 것도 가능하나, 브라우저 환경에서 렌더링된 텍스트를 파싱
        url = f"{self.base_url}/store/goods/getGoodsArtcAjax.do?goodsNo={goods_no}"
        
        try:
            temp_page = await self.context.new_page()
            await temp_page.goto(url, wait_until="domcontentloaded")
            
            # dl > dt(전성분) > dd 추출
            dts = await temp_page.query_selector_all('dt')
            ingredients_text = ""
            for dt in dts:
                dt_text = await dt.inner_text()
                if '전성분' in dt_text or '모든 성분' in dt_text:
                    # 바로 다음 요소인 dd 가져오기
                    dd = await dt.evaluate_handle('node => node.nextElementSibling')
                    if dd:
                        ingredients_text = await dd.inner_text()
                        break
            
            await temp_page.close()
            return ingredients_text.strip()
        except Exception as e:
            return ""

async def main():
    scraper = OliveYoungScraper()
    await scraper.init_browser()
    
    print("스킨케어 제품 검색 중...")
    # 100000100010008 = 스킨/토너 카테고리 예시
    products = await scraper.get_product_list("100000100010008", limit=3)
    
    for p in products:
        print(f"Fetching ingredients for {p['brand']} - {p['name']}...")
        ingredients = await scraper.get_product_ingredients(p['goodsNo'])
        p['ingredients_raw'] = ingredients
        print(f" -> {ingredients[:100]}...")
        # API Rate limit 방지 휴식
        await asyncio.sleep(1)
        
    with open("oliveyoung_sample.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print("완료!")
    
    await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
