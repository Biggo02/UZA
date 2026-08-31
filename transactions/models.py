from django.conf import settings
from django.db import models
from marketplace.models import Listing
import uuid
class PurchaseRequest(models.Model):
    STATUS=[('PENDING','En attente'),('OWNER_ACCEPTED','Acceptée par le propriétaire'),('UZA_APPROVED','Approuvée par UZA'),('SCHEDULED','Planifiée'),('IN_PROGRESS','En cours'),('COMPLETED','Terminée'),('REJECTED','Refusée'),('CANCELLED','Annulée')]
    buyer=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='purchase_requests');listing=models.ForeignKey(Listing,on_delete=models.PROTECT,related_name='purchase_requests');requested_date=models.DateField();requested_time=models.TimeField();message=models.TextField(blank=True);accepted_price=models.DecimalField(max_digits=14,decimal_places=2);owner_decision=models.CharField(max_length=10,default='PENDING');uza_decision=models.CharField(max_length=10,default='PENDING');status=models.CharField(max_length=20,choices=STATUS,default='PENDING');refusal_reason=models.TextField(blank=True);created_at=models.DateTimeField(auto_now_add=True)
class Transaction(models.Model):
    STATUS=[('SCHEDULED','Planifiée'),('IN_PROGRESS','En cours'),('COMPLETED','Terminée'),('CANCELLED','Annulée')]
    reference=models.CharField(max_length=50,unique=True,editable=False);request=models.OneToOneField(PurchaseRequest,on_delete=models.PROTECT,related_name='transaction');appointment_date=models.DateField();appointment_time=models.TimeField();amount_paid=models.DecimalField(max_digits=14,decimal_places=2,default=0);uza_margin=models.DecimalField(max_digits=14,decimal_places=2,default=0);payment_confirmed=models.BooleanField(default=False);handover_confirmed=models.BooleanField(default=False);status=models.CharField(max_length=20,choices=STATUS,default='SCHEDULED')
    def save(self,*a,**kw):
        if not self.reference:self.reference=f'UZA-TRX-{uuid.uuid4().hex[:12].upper()}'
        super().save(*a,**kw)
class Notification(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='notifications');title=models.CharField(max_length=180);message=models.TextField();read=models.BooleanField(default=False);created_at=models.DateTimeField(auto_now_add=True)
class Message(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='uza_messages');body=models.TextField();from_uza=models.BooleanField(default=False);created_at=models.DateTimeField(auto_now_add=True)
class AuditLog(models.Model):
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,related_name='uza_audits');action=models.CharField(max_length=80);object_type=models.CharField(max_length=80);object_id=models.CharField(max_length=80);details=models.JSONField(default=dict,blank=True);created_at=models.DateTimeField(auto_now_add=True)
