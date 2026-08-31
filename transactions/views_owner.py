from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect
from .models import PurchaseRequest,Notification
@login_required
def owner_decision(request,pk,decision):
    r=get_object_or_404(PurchaseRequest,pk=pk,listing__owner=request.user,status='PENDING')
    if decision=='accept':
        r.owner_decision='ACCEPTED';r.status='OWNER_ACCEPTED';r.save();Notification.objects.create(user=r.buyer,title='Le propriétaire a accepté',message=f'Votre demande pour {r.listing.title} a été acceptée. UZA doit encore l’approuver.')
    else:
        r.owner_decision='REJECTED';r.status='REJECTED';r.save();Notification.objects.create(user=r.buyer,title='Demande refusée',message=f'Votre demande pour {r.listing.title} a été refusée.')
    return redirect('dashboard')
