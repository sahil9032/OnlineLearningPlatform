from django.contrib.auth import logout
from django.shortcuts import redirect


def logoutUser(request):
    logout(request)
    return redirect('accounts/login')
