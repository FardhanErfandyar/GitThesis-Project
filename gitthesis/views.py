import subprocess
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Invitation, Project, Collaborator
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
from django.db.models import Q


def project(request):
    return render(request, "project.html")

def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id) 
    return render(request, 'project.html', {'project': project})


def home(request):
    # Get all projects where the user is either the owner or an accepted collaborator
    projects = Project.objects.filter(
        Q(owner=request.user) | Q(collaborator__user=request.user, collaborator__is_accepted=True)
    ).distinct()

    # Get collaborators who are either owners or accepted collaborators in those projects
    collaborators = User.objects.filter(
        Q(owned_projects__in=projects) | Q(collaborator__project__in=projects, collaborator__is_accepted=True)
    ).exclude(id=request.user.id).distinct()
    
    invitations = Collaborator.objects.filter(user=request.user, is_accepted=False)
    
    context = {
        'projects': projects,
        'collaborators': collaborators,
        'invitations': invitations
    }

    return render(request, "home.html", context)



def landing(request):
    return render(request, "landing.html")

@login_required
def profile(request):
    projects = Project.objects.filter(owner=request.user)[:3]
    Contributedprojects = Project.objects.filter(collaborators=request.user)[:3]
    
    # Get all related projects and collaborators without the LIMIT
    all_projects = Project.objects.filter(owner=request.user)
    all_contributed_projects = Project.objects.filter(collaborators=request.user)
    
    # Count the total number of projects (owned and contributed)
    projectcount = all_projects.union(all_contributed_projects).count()
    
    # Get the networks without the LIMIT issue
    networks = User.objects.filter(
        Q(owned_projects__in=all_projects) | 
        Q(collaborator__project__in=all_projects, collaborator__is_accepted=True)
    ).exclude(id=request.user.id).distinct()
    
    networkscount = networks.count()
    
    return render(request, 'profile.html', {'user': request.user, 
                                            'projects': projects, 
                                            'contributedprojects':Contributedprojects,
                                            'projectcount':projectcount,
                                            'networkscount':networkscount,
                                            })


def myprojects(request):
    filter_option = request.GET.get('filter', 'all') 
    order_option = request.GET.get('order', 'latest')  

    # Determine the base queryset based on the filter
    if filter_option == 'mine':
        projects = Project.objects.filter(owner=request.user)
    else:
        projects = Project.objects.filter(collaborators=request.user)

    # Order the projects based on the order option
    if order_option == 'latest':
        projects = projects.order_by('-created_at') 
    else:
        projects = projects.order_by('created_at')  

    return render(request, 'myprojects.html', {'projects': projects})
  

@login_required
def inbox(request):
    invitations = Collaborator.objects.filter(user=request.user, is_accepted=False)

    return render(request, 'inbox.html', {
        'invitations': invitations, 
    })


@login_required
def accept_invitation(request, invitation_id):
    try:
        invitation = Collaborator.objects.get(id=invitation_id, user=request.user, is_accepted=False)
        invitation.is_accepted = True
        invitation.save()
        messages.success(request, "Invitation accepted!")
    except Collaborator.DoesNotExist:
        messages.error(request, "Invitation not found or already accepted.")

    return redirect('inbox')

@login_required
def reject_invitation(request, invitation_id):
    try:
        invitation = Collaborator.objects.get(id=invitation_id, user=request.user)
        invitation.delete()  
        messages.success(request, "Invitation rejected successfully.")
    except Collaborator.DoesNotExist:
        messages.error(request, "Invitation not found or you don't have permission to reject it.")
    
    return redirect('inbox') 

@login_required
def project_settings(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Check if the user is the owner of the project
    if request.user != project.owner:
        return HttpResponseForbidden("You are not allowed to edit this project.")

    if request.method == 'POST':
        collaborators_emails = request.POST.get('collaborators')
        if collaborators_emails:
            emails = [email.strip() for email in collaborators_emails.split(',')]
            
            # Get current collaborators emails for validation
            current_collaborators = project.collaborator_set.all()
            current_collaborator_emails = current_collaborators.values_list('user__email', flat=True)

            # Clear existing collaborators only if they are not accepted
            for collaborator in current_collaborators:
                if not collaborator.is_accepted:
                    collaborator.delete()

            # Add the owner as a collaborator with accepted status if not already present
            if request.user not in [c.user for c in current_collaborators]:
                Collaborator.objects.create(
                    project=project,
                    user=request.user,
                    invited_at=timezone.now(),
                    is_accepted=True
                )

            for email in emails:
                # Skip emails that are already collaborators with is_accepted=False
                if email in current_collaborator_emails:
                    messages.warning(request, f"User with email '{email}' already has an invitation.")
                    continue  # Skip to the next email
                
                try:
                    user = User.objects.get(email=email)
                    if user != request.user:  
                        # Check if the user is already a collaborator
                        if user.email not in current_collaborator_emails:
                            # Only create a collaborator entry if the user is not already a collaborator
                            Collaborator.objects.create(
                                project=project, 
                                user=user, 
                                invited_at=timezone.now(), 
                                is_accepted=False  # Set invitation status to False
                            )
                        else:
                            messages.warning(request, f"User with email '{email}' is already a collaborator.")
                    else:
                        messages.warning(request, "You cannot invite yourself as a collaborator.")
                except User.DoesNotExist:
                    messages.warning(request, f"User with email '{email}' does not exist.")

        messages.success(request, "Collaborators updated successfully!")
        return redirect('project_settings', project_id=project.id)

    # Get all collaborators for the input value
    all_collaborators = project.collaborator_set.all()  # Use reverse relation
    collaboratorsAccepted = all_collaborators.filter(is_accepted=True)  # Get only accepted collaborators

    return render(request, 'project_settings.html', {
        'project': project,
        'all_collaborators': all_collaborators,
        'collaboratorsAccepted': collaboratorsAccepted
    })

@login_required
def remove_collaborator(request, project_id, collaborator_id):
    project = get_object_or_404(Project, id=project_id)

    # Pastikan hanya pemilik proyek yang bisa menghapus kolaborator
    if request.user != project.owner:
        return HttpResponseForbidden("You are not allowed to remove collaborators from this project.")

    try:
        # Dapatkan kolaborator yang ingin dihapus
        collaborator = Collaborator.objects.get(id=collaborator_id, project=project, is_accepted=True)

        # Cek apakah kolaborator yang ingin dihapus adalah pemilik proyek
        if collaborator.user == project.owner:
            messages.error(request, "You cannot remove the project owner.")
            return redirect('project_settings', project_id=project.id)
        
        # Hapus kolaborator dari proyek
        collaborator.delete()

        messages.success(request, f"Collaborator {collaborator.user.username} has been removed successfully.")
    except Collaborator.DoesNotExist:
        messages.error(request, "Collaborator not found or they haven't accepted the invitation yet.")

    return redirect('project_settings', project_id=project.id)


@login_required
def notifications_count(request):
    if request.user.is_authenticated:
        count = Collaborator.objects.filter(user=request.user, is_accepted=False).count()
        return {'invitations_count': count}
    return {'invitations_count': 0}


@login_required
def create_project(request):
    if request.method == 'POST':
        project_name = request.POST.get('projectName')
        collaborator_emails = request.POST.get('collaborators')

        # Validate: Ensure project_name is not empty
        if not project_name:
            messages.error(request, "Project name is required.")
            return render(request, 'createproject.html', {'messages': messages.get_messages(request)})

        # Validate: Ensure project_name length does not exceed 255 characters
        if len(project_name) > 255:
            messages.error(request, "Project name cannot exceed 255 characters.")
            return render(request, 'createproject.html', {'messages': messages.get_messages(request)})

        # Create a new project with the logged-in user as the owner
        project = Project.objects.create(
            name=project_name,
            owner=request.user,  # Set owner as the logged-in user
            created_at=timezone.now(),
        )

        # Add the owner as a collaborator with accepted status
        Collaborator.objects.create(
            project=project, 
            user=request.user, 
            invited_at=timezone.now(), 
            is_accepted=True
        )

        # Add collaborators based on emails
        if collaborator_emails:
            emails = collaborator_emails.split(',')
            for email in emails:
                email = email.strip()
                try:
                    user = User.objects.get(email=email)
                    # Ensure the user is not the owner of the project
                    if user != request.user:  
                        # Create a collaborator entry with is_accepted set to False
                        Collaborator.objects.create(
                            project=project, 
                            user=user, 
                            invited_at=timezone.now(), 
                            is_accepted=False  # Invitation status set to False
                        )
                    else:
                        messages.warning(request, "You cannot invite yourself as a collaborator.")
                except User.DoesNotExist:
                    messages.warning(request, f"User with email '{email}' does not exist.")

        messages.success(request, "Project created successfully! Invitations sent to collaborators.")
        return redirect('myprojects')  # Redirect to the myprojects page after project creation

    return render(request, 'createproject.html')


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
