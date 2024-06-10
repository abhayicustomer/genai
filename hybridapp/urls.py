from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^hybrid/', views.hybrid, name='hybrid'),
    re_path(r'^pdf_view/', views.pdf_view, name='pdf_view'),
    re_path(r'^csv_view/', views.csv_view, name='csv_view'),
]