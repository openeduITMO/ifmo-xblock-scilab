from django.contrib.auth.models import User
from django.db import models


class ScilabSubmission(models.Model):

    STATUS_QUEUED = 'QUEUED'

    user = models.ForeignKey(User, db_index=True)
    sha_1 = models.CharField(max_length=255, db_index=True)
    filename = models.CharField(max_length=255, db_index=True)
    mimetype = models.CharField(max_length=255, default="")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, db_index=True)
    course = models.CharField(max_length=255, db_index=True, default="")
    module = models.CharField(max_length=255, db_index=True, default="")
    size = models.IntegerField(default=0)
    real_filename = models.CharField(max_length=255, default="")