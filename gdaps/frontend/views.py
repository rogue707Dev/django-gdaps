from django.shortcuts import render


def home(request):
    return render(request, "gdaps/application.html", name="app")
