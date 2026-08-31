from django.urls import path
from . import views

urlpatterns = [
    path('', views.recognize, name='product_ai_recognize'),
    path('<int:pk>/confirmer/', views.confirm, name='product_ai_confirm'),
    path('api/', views.api_recognize, name='product_ai_api'),
]
