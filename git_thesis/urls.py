from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from gitthesis.views import landing, home, projects


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", landing),
    path("projects/", projects),
    path("home/", home),
]
