from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404,redirect,render
from .models import Listing,Category,ListingImage
from .forms import ListingForm

def listings(request):
    qs=Listing.objects.filter(status='PUBLISHED').prefetch_related('images');q=request.GET.get('q','').strip();cat=request.GET.get('category','');typ=request.GET.get('type','')
    if q: qs=qs.filter(title__icontains=q)|qs.filter(brand__icontains=q)|qs.filter(model__icontains=q)
    if cat:qs=qs.filter(category__slug=cat)
    if typ:qs=qs.filter(listing_type=typ)
    return render(request,'marketplace/listings.html',{'listings':qs.distinct(),'categories':Category.objects.filter(active=True)})
def detail(request,pk):
    x=get_object_or_404(Listing.objects.prefetch_related('images'),pk=pk,status='PUBLISHED');Listing.objects.filter(pk=pk).update(views=x.views+1);return render(request,'marketplace/detail.html',{'listing':x})
@login_required
def create_listing(request):
    if request.user.verification_status!='VERIFIED':return redirect('verification')
    form=ListingForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        x=form.save(commit=False);x.owner=request.user;x.status='PENDING';x.save()
        for f in request.FILES.getlist('images'):ListingImage.objects.create(listing=x,image=f)
        messages.success(request,'Annonce envoyée à UZA pour validation.');return redirect('dashboard')
    return render(request,'marketplace/create.html',{'form':form})
@login_required
def dashboard(request):
    return render(request,'dashboard.html',{'listings':request.user.listings.all().order_by('-created_at'),'notifications':request.user.notifications.all()[:10]})
