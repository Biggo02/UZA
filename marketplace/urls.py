from django.urls import path
from .views import listings, detail, create_listing, dashboard, analyze_listing_images
urlpatterns = [
    path('annonces/', listings, name='listings'),
    path('annonces/<int:pk>/', detail, name='listing_detail'),
    path('publier/', create_listing, name='create_listing'),
    path('publier/analyser/', analyze_listing_images, name='analyze_listing_images'),
    path('dashboard/', dashboard, name='dashboard'),
]
