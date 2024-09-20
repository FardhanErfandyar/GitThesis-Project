from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from gitthesis.views import *
from django.contrib.auth.views import LoginView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", landing),
    path("project/", project),
    path("home/", home),
    path("myprojects/", myprojects),
    path("myprojects/1", project),
]
