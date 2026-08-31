from django.urls import path
from .views import listings,detail,create_listing,dashboard
urlpatterns=[path('annonces/',listings,name='listings'),path('annonces/<int:pk>/',detail,name='listing_detail'),path('publier/',create_listing,name='create_listing'),path('dashboard/',dashboard,name='dashboard')]
