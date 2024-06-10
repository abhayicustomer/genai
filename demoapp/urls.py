from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^unstructured/', views.unstructured, name='unstructured'),
    re_path(r'^structured/', views.structured, name='structured'),
]