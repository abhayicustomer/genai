# pdfupload/forms.py
from django import forms
from .models import PDF

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDF
        fields = ['file', 'session_id']

