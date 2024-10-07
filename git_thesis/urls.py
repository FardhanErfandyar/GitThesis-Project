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
    path("myprojects/", myprojects),
    path("myprojects/1", project),
    path("preview/", views.preview_latex, name="preview_latex"),
    path("login/", login_view, name="login"),
    path("logout/", custom_logout, name="logout"),
]


from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
