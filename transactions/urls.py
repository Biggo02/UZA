from django.urls import path
from .views import request_purchase,my_transactions
urlpatterns=[path('annonces/<int:pk>/demander/',request_purchase,name='request_purchase'),path('transactions/',my_transactions,name='transactions')]
