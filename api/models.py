# Django imports
from django.db import models


class Ports(models.Model):
    code        = models.CharField(models.Model, primary_key=True, max_length=200)
    name        = models.CharField(models.Model, max_length=200)
    parent_slug = models.CharField(models.Model, max_length=200)


class Prices(models.Model):
    orig_code   = models.CharField(models.Model, primary_key=True, max_length=200)
    dest_code   = models.CharField(models.Model, max_length=200)
    day         = models.DateField(models.Model, max_length=200)
    price       = models.IntegerField(models.Model)


class Regions(models.Model):
    slug        = models.CharField(models.Model, primary_key=True, max_length=200)
    name        = models.CharField(models.Model, max_length=200)
    parent_slug = models.CharField(models.Model, max_length=200)
