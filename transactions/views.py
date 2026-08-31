from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.shortcuts import get_object_or_404,redirect,render
from marketplace.models import Listing
from .forms import PurchaseRequestForm
from .models import PurchaseRequest,Transaction,Notification,AuditLog
@login_required
def request_purchase(request,pk):
    if request.user.verification_status!='VERIFIED':return redirect('verification')
    listing=get_object_or_404(Listing,pk=pk,status='PUBLISHED')
    if listing.owner_id==request.user.id:return redirect('listing_detail',pk=pk)
    form=PurchaseRequestForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        r=form.save(commit=False);r.buyer=request.user;r.listing=listing;r.accepted_price=listing.final_price;r.save();Notification.objects.create(user=listing.owner,title='Nouvelle demande d’achat',message=f'Demande reçue pour {listing.title}.');return redirect('dashboard')
    return render(request,'transactions/request.html',{'listing':listing,'form':form})
@login_required
def my_transactions(request):
    return render(request,'transactions/list.html',{'items':Transaction.objects.filter(request__buyer=request.user).select_related('request','request__listing')})
