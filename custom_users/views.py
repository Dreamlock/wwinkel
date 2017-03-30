from django.shortcuts import render

# Create your views here.

from django.contrib.auth import views, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from .forms import LoginForm

@login_required
def logout_view(request):
    print("hier")
    logout(request)
    return redirect('/')

def login_view(request):
    # if this is a POST request we need to process the form data
    form = None
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            pass


            # redirect to a new URL:
    return render(request,"custom_users/login.html", {'form': form})
