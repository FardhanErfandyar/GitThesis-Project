from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from gitthesis.views import home, projects


urlpatterns = [
    path("admin/", admin.site.urls),
    path("projects/", projects),
    path("", home),
]
