import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    """메인 페이지 렌더링"""
    return render(request, 'index.html')

def search(request):
    """사용자 입력 키워드로 한국관광공사 API 호출 후 결과 반환 (모든 결과 가져오기)"""
    keyword = request.GET.get('keyword')
    if not keyword:
        return JsonResponse([], safe=False)

    api_url = "http://apis.data.go.kr/B551011/KorService1/searchKeyword1"
    
    # 기본 파라미터 설정 (페이지 번호와 한 페이지에 표시할 행 수는 별도로 지정)
    base_params = {
        "serviceKey": settings.KOREA_TOUR_API_KEY,  # settings에 저장한 API 키 사용
        "MobileOS": "ETC",
        "MobileApp": "AppTest",
        "_type": "json",
        "listYN": "Y",
        "arrange": "C",
        "contentTypeId": 38,
        "keyword": keyword,
    }
    
    # API가 한 번에 반환하는 최대 결과 수 (API 문서에서 허용하는 최대값이 있다면 그 값 사용)
    numOfRows = 100
    pageNo = 1
    base_params["numOfRows"] = numOfRows
    base_params["pageNo"] = pageNo

    all_items = []
    
    while True:
        response = requests.get(api_url, params=base_params)
        if response.status_code != 200:
            return JsonResponse({'error': f"API request failed with status code {response.status_code}"}, status=500)
        
        try:
            data = response.json()
        except ValueError:
            print("Failed to decode JSON. Response text:", response.text)
            return JsonResponse({'error': 'Invalid JSON response from API'}, status=500)
        
        # API 응답에서 항목 추출
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        # 만약 항목이 한 개이면 API에 따라 dict로 반환할 수 있으므로 리스트로 변환
        if isinstance(items, dict):
            items = [items]
        
        all_items.extend(items)
        
        # 전체 결과 수 확인 (API 문서에 totalCount 필드가 있다고 가정)
        totalCount = data.get("response", {}).get("body", {}).get("totalCount", 0)
        
        # 모든 항목을 다 가져왔다면 반복 종료
        if len(all_items) >= totalCount:
            break
        
        # 다음 페이지 요청을 위해 pageNo 증가
        pageNo += 1
        base_params["pageNo"] = pageNo

    # 필요한 데이터만 추출하여 결과 리스트 구성
    result = []
    for item in all_items:
        result.append({
            "title": item.get("title", "정보 없음"),
            "addr1": item.get("addr1", "주소 없음"),
            "firstimage": item.get("firstimage", "https://via.placeholder.com/300"),  # 이미지 없으면 기본 이미지 사용
            "mapx": item.get("mapx"),
            "mapy": item.get("mapy")
        })

    return JsonResponse(result, safe=False)