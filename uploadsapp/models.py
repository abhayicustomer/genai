# pdfupload/models.py
from django.db import models
import os
from datetime import datetime
import uuid
# from django.utils.crypto import get_random_string

def user_directory_path(instance, filename):
    session_folder = os.path.join(instance.session_id, "data")
    # unique_filename = f"{uuid.uuid4().hex}_{filename}"
    return os.path.join(session_folder, filename)

# def validate_doc_size(value):
#     filesize= value.size
#     if filesize > 5242880:
#         raise ValidationError("The maximum document size that can be uploaded is 5MB")
#     else:
#         return value

# document = models.FileField(upload_to=the_upload_path, null=True, blank=True, validators=[validate_doc_size])

class PDF(models.Model):
    file = models.FileField(upload_to=user_directory_path)
    session_id = models.CharField(null=True, blank=True, max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
