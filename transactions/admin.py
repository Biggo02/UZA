from django.contrib import admin
from .models import PurchaseRequest,Transaction,Notification,Message,AuditLog
admin.site.register([PurchaseRequest,Transaction,Notification,Message,AuditLog])
