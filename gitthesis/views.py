import subprocess
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Project, Collaborator
from django.contrib.auth.models import User
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


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


def myprojects(request):
    return render(request, "myprojects.html")


def project(request):
    return render(request, "project.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Successfully login")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("landing")

    return render(request, "landing.html")


def custom_logout(request):
    logout(request)
    return redirect("landing")


def invite_user(request, project_id, user_id):
    project = Project.objects.get(id=project_id)
    user_to_invite = User.objects.get(id=user_id)

    # Undang user
    invitation = Collaborator.objects.create(
        project=project,
        user=user_to_invite,
        invited_at=timezone.now(),
        is_accepted=False,
    )
    return redirect("project_detail", project_id=project_id)


def accept_invitation(request, invitation_id):
    invitation = Collaborator.objects.get(id=invitation_id)
    invitation.is_accepted = True
    invitation.save()
    return redirect("project_detail", project_id=invitation.project.id)


# LATEX
def preview_latex(request):
    latex_preview_url = None
    form = LaTeXForm()

    if request.method == "POST":
        form = LaTeXForm(request.POST)
        if form.is_valid():
            # Ambil konten LaTeX dari form
            latex_content = form.cleaned_data["latex_content"]

            # Path untuk menyimpan file LaTeX dan PDF
            latex_file_path = os.path.join(settings.MEDIA_ROOT, "temp_latex.tex")
            pdf_file_path = os.path.join(settings.MEDIA_ROOT, "temp_latex.pdf")

            # Simpan konten LaTeX ke file sementara
            with open(latex_file_path, "w") as f:
                f.write(latex_content)

            # Jalankan pdflatex untuk mengonversi LaTeX ke PDF
            result = subprocess.run(
                ["pdflatex", "-output-directory", settings.MEDIA_ROOT, latex_file_path]
            )

            # Cek apakah file PDF berhasil dihasilkan
            if os.path.exists(pdf_file_path):
                # URL ke PDF hasil preview
                latex_preview_url = os.path.join(settings.MEDIA_URL, "temp_latex.pdf")

    return render(
        request, "template.html", {"form": form, "latex_preview_url": latex_preview_url}
    )
