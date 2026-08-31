from django.contrib import admin
from django.utils import timezone
from .models import Category,Listing,ListingImage
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):list_display=['name','slug','active'];prepopulated_fields={'slug':('name',)};list_filter=['active']
class ImageInline(admin.TabularInline):model=ListingImage;extra=0
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display=['title','owner','category','listing_type','owner_price','margin','final_price','status','views','created_at'];list_filter=['status','listing_type','category'];search_fields=['title','brand','model','reference'];inlines=[ImageInline]
    actions=['publish_selected','suspend_selected']
    @admin.action(description='Publier les annonces sélectionnées')
    def publish_selected(self,request,queryset):queryset.update(status='PUBLISHED')
    @admin.action(description='Suspendre les annonces sélectionnées')
    def suspend_selected(self,request,queryset):queryset.update(status='SUSPENDED')
