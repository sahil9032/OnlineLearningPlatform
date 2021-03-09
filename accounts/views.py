from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect

# Create your views here.
from accounts.forms import CreateUserForm


def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')

    return render(request, 'login.html')


def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name=form.cleaned_data.get('role'))
            user.groups.add(group)
            messages.success(request, 'Account was created for ' + username)
            return redirect('/accounts/login')
    return render(request, 'register.html', context={'form': form})
