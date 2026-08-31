from django.conf import settings
from django.db import models
from django.utils.text import slugify
import uuid

class Category(models.Model):
    name=models.CharField(max_length=120,unique=True);slug=models.SlugField(unique=True);active=models.BooleanField(default=True)
    def save(self,*a,**kw): self.slug=slugify(self.name);super().save(*a,**kw)
    def __str__(self):return self.name
class Listing(models.Model):
    TYPE=[('NEW','Neuf'),('USED','Seconde main')];STATUS=[('DRAFT','Brouillon'),('PENDING','En vérification'),('PUBLISHED','Publiée'),('SUSPENDED','Suspendue'),('REJECTED','Refusée'),('SOLD','Vendue'),('ARCHIVED','Archivée')]
    owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='listings');category=models.ForeignKey(Category,on_delete=models.PROTECT,related_name='listings');listing_type=models.CharField(max_length=8,choices=TYPE)
    title=models.CharField(max_length=180);brand=models.CharField(max_length=100);model=models.CharField(max_length=120);reference=models.CharField(max_length=80,blank=True);description=models.TextField()
    owner_price=models.DecimalField(max_digits=14,decimal_places=2);margin=models.DecimalField(max_digits=14,decimal_places=2,default=0);final_price=models.DecimalField(max_digits=14,decimal_places=2,default=0)
    city=models.CharField(max_length=100,default='Lubumbashi');specifications=models.JSONField(default=dict,blank=True);status=models.CharField(max_length=12,choices=STATUS,default='DRAFT');refusal_reason=models.TextField(blank=True);views=models.PositiveIntegerField(default=0);created_at=models.DateTimeField(auto_now_add=True);updated_at=models.DateTimeField(auto_now=True)
    def save(self,*a,**kw):
        self.final_price=self.owner_price+self.margin
        if not self.reference:self.reference=f'UZA-{uuid.uuid4().hex[:10].upper()}'
        super().save(*a,**kw)
class ListingImage(models.Model):
    listing=models.ForeignKey(Listing,on_delete=models.CASCADE,related_name='images');image=models.ImageField(upload_to='listings/%Y/%m/');sort_order=models.PositiveIntegerField(default=0);caption=models.CharField(max_length=120,blank=True)
