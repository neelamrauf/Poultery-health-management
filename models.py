from django.conf import settings
from django.db import models


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Order #{self.id} by {self.farmer} on {self.submitted_at:%Y-%m-%d}"


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    medicine = models.ForeignKey(
        "inventory.Medicine",
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.medicine} (Order #{self.order_id})"
