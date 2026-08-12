from django.urls import path
from .views import LSASearchView, LSACreateView

urlpatterns = [
    path('', LSACreateView.as_view(), name='lsa-create'),
    path('search/', LSASearchView.as_view(), name='lsa-search'),
]
