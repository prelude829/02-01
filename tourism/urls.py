# tourism/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),       # 메인 페이지
    path('search', views.search, name='search'), # 검색 API 엔드포인트
]
