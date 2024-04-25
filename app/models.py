from django.db import models



class PatentData(models.Model):
    name = models.CharField(max_length=100, null=True)
    age = models.CharField(max_length=100, null=True)
    weight = models.CharField(max_length=100, null=True)
    symptoms = models.TextField(null=True)
    recdata = models.TextField(null=True)

  
