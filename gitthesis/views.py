from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Project, ProjectCollaborator
from django.contrib.auth.models import User

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


def invite_user(request, project_id, user_id):
    project = Project.objects.get(id=project_id)
    user_to_invite = User.objects.get(id=user_id)

    # Undang user
    invitation = ProjectCollaborator.objects.create(
        project=project,
        user=user_to_invite,
        invited_at=timezone.now(),
        is_accepted=False,
    )
    return redirect("project_detail", project_id=project_id)


def accept_invitation(request, invitation_id):
    invitation = ProjectCollaborator.objects.get(id=invitation_id)
    invitation.is_accepted = True
    invitation.save()
    return redirect("project_detail", project_id=invitation.project.id)
