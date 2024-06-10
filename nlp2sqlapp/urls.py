from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^nlp2sql/', views.nlp2sql, name='nlp2sql'),
]