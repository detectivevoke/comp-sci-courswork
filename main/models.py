from django.db import models

class UploadedFolder(models.Model):
    folder = models.FileField(upload_to='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class UploadedFile(models.Model):
    folder = models.FileField