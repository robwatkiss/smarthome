from django.db import models

class Entry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    source = models.CharField(max_length=128, db_index=True)
    field = models.CharField(max_length=64, db_index=True)
    value = models.FloatField()