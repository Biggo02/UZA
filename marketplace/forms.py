from django import forms
from .models import Listing,ListingImage
class ListingForm(forms.ModelForm):
    class Meta:
        model=Listing;fields=['category','listing_type','title','brand','model','reference','description','owner_price','city','specifications']
        widgets={'specifications':forms.HiddenInput()}
class ListingImageForm(forms.ModelForm):
    class Meta:model=ListingImage;fields=['image','caption']
