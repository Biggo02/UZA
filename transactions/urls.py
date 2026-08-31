from django.urls import path
from .views import request_purchase,my_transactions
from .views_owner import owner_decision
urlpatterns=[path('annonces/<int:pk>/demander/',request_purchase,name='request_purchase'),path('transactions/',my_transactions,name='transactions'),path('demandes/<int:pk>/<str:decision>/',owner_decision,name='owner_decision')]
