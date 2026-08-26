from django.db import models
from django.conf import settings


GOVERNORATE_CHOICES = [
    ("damascus", "Damascus"),
    ("aleppo", "Aleppo"),
    ("homs", "Homs"),
    ("hama", "Hama"),
    ("latakia", "Latakia"),
    ("tartus", "Tartus"),
    ("idlib", "Idlib"),
    ("raqqa", "Raqqa"),
    ("deir_ezzor", "Deir_Ezzor"),
    ("hasakah", "Hasakah"),
    ("daraa", "Daraa"),
    ("suwayda", "Suwayda"),
    ("quneitra", "Quneitra"),
]


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    phone_number = models.CharField(max_length=20)
    governorate = models.CharField(max_length=20,choices=GOVERNORATE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(
        upload_to="products/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.name} image"