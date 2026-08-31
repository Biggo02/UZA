from django.contrib import admin
from django.utils import timezone
from .models import User,Verification
@admin.register(User)
class UserAdmin(admin.ModelAdmin):list_display=['username','first_name','last_name','phone','verification_status','role','date_joined'];list_filter=['verification_status','role'];search_fields=['username','phone','email','first_name','last_name']
@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display=['user','document_type','decision','created_at','reviewed_at'];list_filter=['decision','document_type'];search_fields=['user__username','document_number']
    actions=['approve','reject_without_reason']
    @admin.action(description='Certifier les dossiers sélectionnés')
    def approve(self,request,queryset):
        for v in queryset.filter(decision='PENDING'):v.decision='APPROVED';v.reviewed_at=timezone.now();v.save();v.user.verification_status='VERIFIED';v.user.save(update_fields=['verification_status'])
    @admin.action(description='Refuser (à compléter avec motif)')
    def reject_without_reason(self,request,queryset):
        queryset.update(decision='REJECTED',reviewed_at=timezone.now())
