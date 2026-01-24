from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .services.skolaonline import fetch_grades
from .models import SkolaOnlineProfile
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import LoginForm
from collections import defaultdict

@login_required
def dashboard(request):
    error = None
    grades_by_subject = {}

    try:
        profile = SkolaOnlineProfile.objects.get(user=request.user)
    except SkolaOnlineProfile.DoesNotExist:
        error = "No SkolaOnline profile found."
        return render(request, "grades/dashboard.html", {"error": error})

    grades = fetch_grades(profile.sol_username, profile.sol_password)
    if not grades:
        error = "Failed to fetch grades. Check your credentials."
        return render(request, "grades/dashboard.html", {"error": error})

    grades_by_subject = defaultdict(list)
    for g in grades:
        grades_by_subject[g["Predmet"]].append({
            "Datum": g["Datum"],
            "Tema": g["Tema"],
            "Vaha": g["Vaha"],
            "Vysledek": g["Vysledek"],
            "Slovni_hodnoceni": g["Slovni_hodnoceni"]
        })

    return render(request, "grades/dashboard.html", {
        "grades_by_subject": dict(grades_by_subject),
        "error": error
    })


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            sol_username = form.cleaned_data["sol_username"]
            sol_password = form.cleaned_data["sol_password"]

            user, created = User.objects.get_or_create(username=sol_username)
            user.set_password("temporary")
            user.save()

            profile, _ = SkolaOnlineProfile.objects.get_or_create(user=user)
            profile.sol_username = sol_username
            profile.sol_password = sol_password
            profile.save()

            login(request, user)
            return redirect("dashboard")

    else:
        form = LoginForm()

    return render(request, "grades/login.html", {"form": form})
