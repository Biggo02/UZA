from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Verification
class RegisterForm(UserCreationForm):
    class Meta: model=User; fields=['first_name','last_name','username','phone','email','city','password1','password2']
class LoginForm(AuthenticationForm):
    username=forms.CharField(label='Nom d’utilisateur')
class VerificationForm(forms.ModelForm):
    class Meta:
        model=Verification; fields=['document_type','document_number','front','back','selfie']
        widgets={x:forms.ClearableFileInput(attrs={'accept':'image/*'}) for x in ['front','back','selfie']}
