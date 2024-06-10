from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^rag/', views.rag, name='rag'),
]