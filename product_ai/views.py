from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProductRecognitionForm, ProductRecognitionConfirmForm
from .models import ProductRecognition
from .services import recognize_product

@login_required
def recognize(request):
    if request.method == 'POST':
        form = ProductRecognitionForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            try:
                result = recognize_product(obj.image.path)
                obj.detected_category = result['category']
                obj.detected_brand = result['brand']
                obj.detected_model = result['model']
                obj.detected_reference = result['reference']
                obj.extracted_text = result['text']
                obj.confidence = result['confidence']
                obj.raw_result = result
                obj.status = 'DONE'
            except Exception as exc:
                obj.status = 'FAILED'
                obj.raw_result = {'error': str(exc)}
            obj.save()
            return redirect('product_ai_confirm', pk=obj.pk)
    else:
        form = ProductRecognitionForm()
    return render(request, 'product_ai/recognize.html', {'form': form})

@login_required
def confirm(request, pk):
    obj = get_object_or_404(ProductRecognition, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProductRecognitionConfirmForm(request.POST)
        if form.is_valid():
            obj.detected_category = form.cleaned_data['category']
            obj.detected_brand = form.cleaned_data['brand']
            obj.detected_model = form.cleaned_data['model']
            obj.detected_reference = form.cleaned_data['reference']
            obj.confirmed = True
            obj.save(update_fields=['detected_category','detected_brand','detected_model','detected_reference','confirmed'])
            return redirect('create_listing')
    else:
        form = ProductRecognitionConfirmForm(initial={'category':obj.detected_category,'brand':obj.detected_brand,'model':obj.detected_model,'reference':obj.detected_reference})
    return render(request, 'product_ai/confirm.html', {'object':obj,'form':form})

@login_required
def api_recognize(request):
    if request.method != 'POST' or 'image' not in request.FILES:
        return JsonResponse({'error':'Une image est requise.'}, status=400)
    temp = ProductRecognition.objects.create(user=request.user, image=request.FILES['image'])
    try:
        result = recognize_product(temp.image.path)
        temp.detected_category=result['category']; temp.detected_brand=result['brand']; temp.detected_model=result['model']; temp.extracted_text=result['text']; temp.confidence=result['confidence']; temp.raw_result=result; temp.status='DONE'; temp.save()
        return JsonResponse(result)
    except Exception as exc:
        temp.status='FAILED'; temp.raw_result={'error':str(exc)}; temp.save()
        return JsonResponse({'error':'Analyse impossible.'}, status=500)
