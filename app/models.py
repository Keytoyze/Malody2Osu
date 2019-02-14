from django.db import models
from project import settings
import os


# Create your models here.
class ConvModel(models.Model):
    conv_id = models.AutoField(primary_key=True)
    datetime = models.DateTimeField(auto_now=True)
    in_file = models.TextField(null=True)
    out_file = models.TextField(null=True)
    result = models.BooleanField(null=True)

    def get_absolute(self, filename):
        dir = os.path.join(settings.FILES_DIR, str(self.conv_id))
        if not os.path.exists(dir):
            os.makedirs(dir)
        return os.path.join(dir, filename)
