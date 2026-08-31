from django.urls import path
from .views import register,signin,signout,verification
urlpatterns=[path('inscription/',register,name='register'),path('connexion/',signin,name='login'),path('deconnexion/',signout,name='logout'),path('verification/',verification,name='verification')]
