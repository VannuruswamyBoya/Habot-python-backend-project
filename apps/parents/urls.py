from django.urls import path
from .views import UserRegisterView, ParentCreateView

urlpatterns = [
    path('', ParentCreateView.as_view(), name='parent-create'),
    path('register/', UserRegisterView.as_view(), name='user-register'),
]
