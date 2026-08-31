from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES=[('USER','Utilisateur'),('STAFF','Staff UZA'),('ADMIN','Administrateur')]
    role=models.CharField(max_length=10,choices=ROLE_CHOICES,default='USER')
    phone=models.CharField(max_length=30,unique=True)
    city=models.CharField(max_length=100,default='Lubumbashi')
    address_general=models.CharField(max_length=255,blank=True)
    avatar=models.ImageField(upload_to='profiles/',blank=True,null=True)
    verification_status=models.CharField(max_length=15,choices=[('UNVERIFIED','Non vérifié'),('PENDING','En vérification'),('VERIFIED','Certifié'),('SUSPENDED','Suspendu')],default='UNVERIFIED')
    def __str__(self): return self.get_full_name() or self.username

class Verification(models.Model):
    TYPES=[('ID','Carte d’identité'),('PASSPORT','Passeport'),('DRIVER','Permis de conduire')]
    DECISIONS=[('PENDING','En attente'),('APPROVED','Approuvé'),('REJECTED','Refusé')]
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='verifications')
    document_type=models.CharField(max_length=20,choices=TYPES)
    document_number=models.CharField(max_length=100)
    front=models.ImageField(upload_to='private_kyc/')
    back=models.ImageField(upload_to='private_kyc/',blank=True,null=True)
    selfie=models.ImageField(upload_to='private_kyc/')
    decision=models.CharField(max_length=20,choices=DECISIONS,default='PENDING')
    refusal_reason=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    reviewed_at=models.DateTimeField(null=True,blank=True)
    class Meta: ordering=['-created_at']
