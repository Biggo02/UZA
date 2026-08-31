from django.contrib import admin
from .models import ProductRecognition

@admin.register(ProductRecognition)
class ProductRecognitionAdmin(admin.ModelAdmin):
    list_display = ('id','user','detected_brand','detected_model','confidence','status','confirmed','created_at')
    list_filter = ('status','confirmed','detected_brand')
    search_fields = ('detected_brand','detected_model','detected_reference','extracted_text')
    readonly_fields = ('extracted_text','raw_result','confidence','created_at')
