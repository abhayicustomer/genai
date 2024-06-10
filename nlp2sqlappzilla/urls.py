from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^nlp2sqlzilla/', views.nlp2sqlzilla, name='nlp2sqlzilla'),
]