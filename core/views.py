from django.db import OperationalError
from django.http import JsonResponse
from django.shortcuts import render
from marketplace.models import Listing, Category


def home(request):
    # The landing page must remain renderable even while the local database
    # container is starting. This prevents a broken DB from masking the UI.
    try:
        recent = Listing.objects.filter(status='PUBLISHED').order_by('-created_at')[:8]
        categories = Category.objects.filter(active=True)
        # Force evaluation here so connection errors are caught before render.
        recent = list(recent)
        categories = list(categories)
    except OperationalError:
        recent = []
        categories = []
    return render(request, 'home.html', {'recent': recent, 'categories': categories})


def health(request):
    return JsonResponse({'status': 'ok', 'service': 'UZA Django'})
