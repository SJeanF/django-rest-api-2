from django.db import models
from . import Category


class Product(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    price = models.PositiveIntegerField(null=True)
    active = models.BooleanField(default=True)
    category = models.ManyToManyField(Category, blank=True)
