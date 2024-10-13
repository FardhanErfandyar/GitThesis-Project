from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from gitthesis import views
from gitthesis.views import *
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", landing, name="landing"),
    path("project/", project),
    path("home/", home, name="home"),
    path('profile/', views.profile, name='profile'),
    path("myprojects/", myprojects, name='myprojects'),
    path('myprojects/project/<int:project_id>/', views.project_detail, name='project_detail'),
    path("preview/", views.preview_latex, name="preview_latex"),
    path("login/", login_view, name="login"),
    path("register/", register, name="register"),
    path("logout/", custom_logout, name="logout"),
    path("myprojects/createnewproject/", create_project, name="create_project"),
    path("myprojects/project/<int:project_id>/settings/", project_settings, name="project_settings"),
    path('inbox/', inbox, name='inbox'),
    path('accept_invitation/<int:invitation_id>/', accept_invitation, name='accept_invitation'),
    path('reject_invitation/<int:invitation_id>/', reject_invitation, name='reject_invitation'),
    path('project/<int:project_id>/remove-collaborator/<int:collaborator_id>/', views.remove_collaborator, name='remove_collaborator'),


    
]


from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
