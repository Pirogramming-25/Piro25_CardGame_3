from django.contrib.auth import login
from django.shortcuts import redirect, render


def signup(request):
    # Step 9에서 완성
    return render(request, "accounts/signup.html")