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
    path("myprojects/", myprojects, name='myprojects'),
    path('project/<int:id>/', views.project_detail, name='project_detail'),
    path("preview/", views.preview_latex, name="preview_latex"),
    path("login/", login_view, name="login"),
    path("register/", register, name="register"),
    path("logout/", custom_logout, name="logout"),
    path("createproject/", createproject, name="createproject"),
    path("createnewproject/", create_project, name="create_project"),
    path("project/<int:project_id>/settings/", project_settings, name="project_settings"),

    
]


from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
