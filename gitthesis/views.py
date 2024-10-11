import subprocess
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Project, Collaborator
from django.contrib.auth.models import User
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from gitthesis.forms import CustomUserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404


def project(request):
    return render(request, "project.html")

def project_detail(request, id):
    project = get_object_or_404(Project, id=id)  # Fetch the project by ID
    return render(request, 'project.html', {'project': project})  # Render the project detail template


def home(request):
    return render(request, "home.html")


def landing(request):
    return render(request, "landing.html")


def myprojects(request):
    # Ambil proyek yang dimiliki oleh pengguna yang sedang login
    projects = Project.objects.filter(owner=request.user)  # Ambil proyek yang dimiliki pengguna
    
    return render(request, 'myprojects.html', {'projects': projects})  # Kirim proyek ke template



def createproject(request):
    return render(request, "createproject.html")

@login_required
def project_settings(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if the user is the owner of the project
    if request.user != project.owner:
        return HttpResponseForbidden("You are not allowed to edit this project.")

    if request.method == 'POST':
        # Handle collaborator updates
        collaborators_emails = request.POST.get('collaborators')
        if collaborators_emails:
            emails = [email.strip() for email in collaborators_emails.split(',')]
            # Clear existing collaborators
            project.collaborators.clear()
            for email in emails:
                try:
                    user = User.objects.get(email=email)
                    project.collaborators.add(user)
                except User.DoesNotExist:
                    messages.warning(request, f"User with email '{email}' does not exist.")
        
        messages.success(request, "Collaborators updated successfully!")
        return redirect('project_settings', project_id=project.id)

    collaborators = project.collaborators.all()
    return render(request, 'project_settings.html', {'project': project, 'collaborators': collaborators})

@login_required
def create_project(request):
    if request.method == 'POST':
        project_name = request.POST.get('projectName')
        collaborator_emails = request.POST.get('collaborators')

        # Validasi: Pastikan project_name tidak kosong
        if not project_name:
            messages.error(request, "Project name is required.")
            return render(request, 'createproject.html', {'messages': messages.get_messages(request)})

        # Validasi: Pastikan panjang project_name tidak lebih dari 255 karakter
        if len(project_name) > 255:
            messages.error(request, "Project name cannot exceed 255 characters.")
            return render(request, 'createproject.html', {'messages': messages.get_messages(request)})

        # Buat project baru dengan owner sebagai user yang login
        project = Project.objects.create(
            name=project_name,
            owner=request.user,  # Set owner sebagai user yang login
            created_at=timezone.now(),
        )

        # Tambahkan owner sebagai kolaborator
        Collaborator.objects.create(
            project=project, 
            user=request.user, 
            invited_at=timezone.now(), 
            is_accepted=True
        )

        # Tambahkan kolaborator berdasarkan email
        if collaborator_emails:
            emails = collaborator_emails.split(',')
            for email in emails:
                email = email.strip()
                try:
                    user = User.objects.get(email=email)
                    Collaborator.objects.create(
                        project=project, 
                        user=user, 
                        invited_at=timezone.now()
                    )
                except User.DoesNotExist:
                    messages.warning(request, f"User with email '{email}' does not exist.")

        messages.success(request, "Project created successfully!")
        return redirect('myprojects')  # Redirect ke halaman myprojects setelah project dibuat

    return render(request, 'createproject.html')


# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             messages.success(request, "Successfully login")
#             return redirect("home")
#         else:
#             messages.error(request, "Invalid username or password.")
#             return redirect("landing")


#     return render(request, "landing.html")


# def register(request):
#     if request.method == "POST":
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             return JsonResponse({"success": True})
#         else:
#             return JsonResponse({"success": False, "error": form.errors.as_json()})

#     form = CustomUserCreationForm()
#     return render(request, "landing.html", {"form": form})


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        errors = {}

        # Validasi username
        if not username:
            errors["username"] = "Username is required"
        elif User.objects.filter(username=username).exists():
            errors["username"] = "Username already exists"

        # Validasi email
        if not email:
            errors["email"] = "Email is required"
        else:
            try:
                validate_email(email)
                if User.objects.filter(email=email).exists():
                    errors["email"] = "Email already exists"
            except ValidationError:
                errors["email"] = "Enter a valid email address"

        # Validasi password
        if not password1 or not password2:
            errors["password"] = "Password is required"
        elif password1 != password2:
            errors["password"] = "Passwords do not match"
        else:
            try:
                validate_password(password1)
            except ValidationError as e:
                errors["password"] = list(e.messages)

        if errors:
            return JsonResponse({"success": False, "error": errors})

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password1),
        )

        return JsonResponse({"success": True})

    return render(request, "landing.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"success": True})
        else:
            return JsonResponse(
                {"success": False, "error": "Invalid username or password."}
            )

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
