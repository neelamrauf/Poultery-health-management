from django.core.validators import MinValueValidator
from django.db import models


class Medicine(models.Model):
    """
    Represents a medicine product in the inventory.

    Tracks stock, dosage information, pricing, and expiry for each medicine
    a Farmer holds on hand.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=100)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    stock_quantity = models.IntegerField(
        validators=[MinValueValidator(0)],
    )
    dosage_per_bird = models.FloatField(
        validators=[MinValueValidator(0.000001)],  # strictly > 0
    )
    dosage_unit = models.CharField(max_length=50)  # e.g. "ml", "g"
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name
