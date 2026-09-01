from pathlib import Path
from uuid import uuid4
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from PIL import Image, ImageOps, UnidentifiedImageError
from .forms import ListingForm
from .models import Listing, Category, ListingImage
from .vision import analyze_images

TEMP_DIR = Path(settings.MEDIA_ROOT) / '.uza_uploads'
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_PIXELS = 30_000_000

def _temp_files(request):
    return request.session.get('uza_photo_files', {})

def _save_temp_photo(uploaded, user_id, slot):
    if uploaded.size > MAX_UPLOAD_BYTES:
        raise ValueError('Cette photo dépasse 25 Mo.')
    try:
        with Image.open(uploaded) as source:
            source.verify()
        uploaded.seek(0)
        with Image.open(uploaded) as source:
            if source.width * source.height > MAX_PIXELS:
                raise ValueError('Cette image possède une résolution trop élevée.')
            source = ImageOps.exif_transpose(source)
            source.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
            if source.mode != 'RGB':
                source = source.convert('RGB')
            folder = TEMP_DIR / str(user_id)
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / f'{uuid4().hex}-photo-{slot}.jpg'
            source.save(path, 'JPEG', quality=78, optimize=True, progressive=True)
            return path
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError('Le fichier n’est pas une image valide ou ne peut pas être traité.') from exc

def _clear_temp(request):
    files = request.session.pop('uza_photo_files', {})
    for value in files.values():
        try: Path(value).unlink(missing_ok=True)
        except OSError: pass

def listings(request):
    qs = Listing.objects.filter(status='PUBLISHED').prefetch_related('images')
    q = request.GET.get('q', '').strip(); cat = request.GET.get('category', ''); typ = request.GET.get('type', '')
    if q: qs = qs.filter(title__icontains=q) | qs.filter(brand__icontains=q) | qs.filter(model__icontains=q)
    if cat: qs = qs.filter(category__slug=cat)
    if typ: qs = qs.filter(listing_type=typ)
    return render(request, 'marketplace/listings.html', {'listings': qs.distinct(), 'categories': Category.objects.filter(active=True)})

def detail(request, pk):
    x = get_object_or_404(Listing.objects.prefetch_related('images'), pk=pk, status='PUBLISHED')
    Listing.objects.filter(pk=pk).update(views=x.views + 1)
    return render(request, 'marketplace/detail.html', {'listing': x})

@login_required
def upload_listing_photo(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'ERROR', 'message': 'Méthode non autorisée.'}, status=405)
    try:
        slot = int(request.POST.get('slot', '0'))
        if slot not in range(1, 6): raise ValueError('Emplacement invalide.')
        uploaded = request.FILES.get('image')
        if not uploaded: raise ValueError('Aucune photo reçue.')
        files = _temp_files(request)
        old = files.get(str(slot))
        if old:
            try: Path(old).unlink(missing_ok=True)
            except OSError: pass
        path = _save_temp_photo(uploaded, request.user.pk, slot)
        files[str(slot)] = str(path)
        request.session['uza_photo_files'] = files
        request.session.modified = True
        return JsonResponse({'status': 'OK', 'slot': slot, 'size': path.stat().st_size, 'count': len(files)})
    except ValueError as exc:
        return JsonResponse({'status': 'ERROR', 'message': str(exc)}, status=400)
    except Exception:
        return JsonResponse({'status': 'ERROR', 'message': 'Impossible de traiter cette photo. Réessayez avec une photo moins lourde.'}, status=500)

@login_required
def analyze_listing_images(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'ERROR', 'message': 'Méthode non autorisée.'}, status=405)
    files = _temp_files(request)
    if set(files.keys()) != {'1', '2', '3', '4', '5'}:
        return JsonResponse({'status': 'ERROR', 'message': 'UZA exige exactement 5 photos traitées.'}, status=400)
    opened = []
    try:
        for slot in range(1, 6):
            path = Path(files[str(slot)])
            if not path.exists(): raise ValueError('Une photo temporaire est introuvable.')
            opened.append(open(path, 'rb'))
        result = analyze_images(opened)
    except Exception:
        result = {'status': 'LOCAL_UNAVAILABLE', 'confidence': 0, 'photo_count': 5, 'message': 'Analyse visuelle temporairement indisponible. Vous pouvez continuer avec une identification manuelle.'}
    finally:
        for f in opened:
            try: f.close()
            except Exception: pass
    return JsonResponse(result)

@login_required
def create_listing(request):
    if request.user.verification_status != 'VERIFIED': return redirect('verification')
    form = ListingForm(request.POST or None)
    temp = _temp_files(request)
    if request.method == 'POST':
        if set(temp.keys()) != {'1', '2', '3', '4', '5'}:
            form.add_error(None, 'Ajoutez et traitez exactement 5 photos avant de soumettre.')
        elif form.is_valid():
            x = form.save(commit=False); x.owner = request.user; x.status = 'PENDING'; x.save()
            for index in range(1, 6):
                path = Path(temp[str(index)])
                with path.open('rb') as fh:
                    ListingImage.objects.create(listing=x, image=File(fh, name=f'uza-photo-{index}.jpg'), sort_order=index)
            _clear_temp(request)
            messages.success(request, 'Annonce envoyée à UZA pour validation.')
            return redirect('dashboard')
    return render(request, 'marketplace/create.html', {'form': form, 'categories': Category.objects.filter(active=True)})

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'listings': request.user.listings.all().order_by('-created_at'), 'notifications': request.user.notifications.all()[:10]})
