from django.conf import settings
from django.db import models

class ProductRecognition(models.Model):
    STATUS_CHOICES = [('PENDING','En attente'),('DONE','Analysée'),('FAILED','Échec')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_recognitions')
    image = models.ImageField(upload_to='product_ai/')
    detected_category = models.CharField(max_length=120, blank=True)
    detected_brand = models.CharField(max_length=120, blank=True)
    detected_model = models.CharField(max_length=180, blank=True)
    detected_reference = models.CharField(max_length=180, blank=True)
    extracted_text = models.TextField(blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    raw_result = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.detected_brand} {self.detected_model}'.strip() or f'Reconnaissance #{self.pk}'
