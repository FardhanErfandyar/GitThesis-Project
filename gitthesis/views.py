from django.shortcuts import render

# Create your views here.


def project(request):

    judul = "coba django"
    isi = ["isi", "asa", "asu"]

    context = {"title": judul, "tai": isi}

    return render(request, "project.html", context)


def home(request):
    return render(request, "home.html")


def landing(request):
    return render(request, "landing.html")
