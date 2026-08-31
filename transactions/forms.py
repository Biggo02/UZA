from django import forms
from .models import PurchaseRequest
class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model=PurchaseRequest;fields=['requested_date','requested_time','message']
        widgets={'requested_date':forms.DateInput(attrs={'type':'date'}),'requested_time':forms.TimeInput(attrs={'type':'time'}),'message':forms.Textarea(attrs={'rows':4})}
