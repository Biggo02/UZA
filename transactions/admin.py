from django.contrib import admin
from .models import PurchaseRequest,Transaction,Notification,Message,AuditLog
@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display=['id','listing','buyer','requested_date','requested_time','owner_decision','uza_decision','status'];list_filter=['status','owner_decision','uza_decision'];search_fields=['listing__title','buyer__username']
    @admin.action(description='Approuver UZA et planifier si vendeur accepté')
    def approve_uza(self,request,queryset):
        for r in queryset:
            if r.owner_decision=='ACCEPTED' and r.status=='OWNER_ACCEPTED':
                r.uza_decision='ACCEPTED';r.status='SCHEDULED';r.save();Transaction.objects.get_or_create(request=r,defaults={'appointment_date':r.requested_date,'appointment_time':r.requested_time,'amount_paid':0,'uza_margin':r.listing.margin});Notification.objects.create(user=r.buyer,title='Transaction planifiée',message=f'Votre rendez-vous UZA pour {r.listing.title} est planifié.');Notification.objects.create(user=r.listing.owner,title='Transaction planifiée',message=f'Le rendez-vous UZA pour {r.listing.title} est planifié.')
    actions=['approve_uza']
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display=['reference','request','appointment_date','appointment_time','amount_paid','uza_margin','payment_confirmed','handover_confirmed','status'];list_filter=['status','payment_confirmed','handover_confirmed'];readonly_fields=['reference']
    @admin.action(description='Terminer les transactions prêtes')
    def complete_selected(self,request,queryset):
        for t in queryset:
            if t.payment_confirmed and t.handover_confirmed and t.status in ['SCHEDULED','IN_PROGRESS']:
                t.status='COMPLETED';t.save();r=t.request;r.status='COMPLETED';r.save();r.listing.status='SOLD';r.listing.save(update_fields=['status']);AuditLog.objects.create(actor=request.user,action='TRANSACTION_COMPLETED',object_type='Transaction',object_id=str(t.pk),details={'reference':t.reference});Notification.objects.create(user=r.buyer,title='Transaction terminée',message=f'La transaction {t.reference} est terminée.');Notification.objects.create(user=r.listing.owner,title='Vente terminée',message=f'La vente {r.listing.title} est terminée.')
    actions=['complete_selected']
admin.site.register([Notification,Message,AuditLog])
