from django.shortcuts import render
from marketplace.models import Listing, Category
def home(request):
    return render(request,'home.html',{'recent':Listing.objects.filter(status='PUBLISHED').order_by('-created_at')[:8],'categories':Category.objects.filter(active=True)})
