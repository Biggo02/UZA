from django import forms
from .models import ProductRecognition

class ProductRecognitionForm(forms.ModelForm):
    class Meta:
        model = ProductRecognition
        fields = ['image']
        widgets = {'image': forms.ClearableFileInput(attrs={'accept':'image/jpeg,image/png,image/webp','capture':'environment'})}

class ProductRecognitionConfirmForm(forms.Form):
    category = forms.CharField(max_length=120, required=False)
    brand = forms.CharField(max_length=120, required=False)
    model = forms.CharField(max_length=180, required=False)
    reference = forms.CharField(max_length=180, required=False)
