from django.contrib import messages
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect,render
from django.utils import timezone
from .forms import RegisterForm,LoginForm,VerificationForm
from .models import Verification

def register(request):
    if request.user.is_authenticated:return redirect('dashboard')
    form=RegisterForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): login(request,form.save()); return redirect('dashboard')
    return render(request,'auth/register.html',{'form':form})
def signin(request):
    if request.user.is_authenticated:return redirect('dashboard')
    form=LoginForm(request=request,data=request.POST or None)
    if request.method=='POST' and form.is_valid(): login(request,form.get_user()); return redirect(request.GET.get('next','dashboard'))
    return render(request,'auth/login.html',{'form':form})
def signout(request): logout(request); return redirect('home')
@login_required
def verification(request):
    if request.user.verification_status=='VERIFIED':return redirect('dashboard')
    form=VerificationForm(request.POST or None,request.FILES or None)
    if request.method=='POST' and form.is_valid():
        v=form.save(commit=False);v.user=request.user;v.save();request.user.verification_status='PENDING';request.user.save(update_fields=['verification_status']);messages.success(request,'Votre dossier a été envoyé à UZA.');return redirect('dashboard')
    return render(request,'auth/verification.html',{'form':form})
