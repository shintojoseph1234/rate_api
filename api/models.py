# Django imports
from django.db import models


class Ports(models.Model):
    code        = models.CharField(models.Model, max_length=5)
    name        = models.CharField(models.Model, max_length=200)
    parent_slug = models.CharField(models.Model, max_length=200)


class Prices(models.Model):
    orig_code   = models.CharField(models.Model, max_length=5)
    dest_code   = models.CharField(models.Model, max_length=5)
    day         = models.DateField(models.Model)
    price       = models.IntegerField(models.Model, default=0)

    def get_price(self):
        return self.price



class Regions(models.Model):
    slug        = models.CharField(models.Model, max_length=200)
    name        = models.CharField(models.Model, max_length=200)
    parent_slug = models.CharField(models.Model, max_length=200)
