from django.db import models


class Algorithm(models.Model):
    title = models.CharField(max_length=128, default='')

    def __str__(self):
        return self.title