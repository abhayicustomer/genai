# pdfupload/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('upload/', upload_pdf, name='upload_pdf'),
    path('upload_csv/', upload_csv, name='upload_csv'),
]
