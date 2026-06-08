"""
Serializers for the Orders app.

Handles checkout (POST /api/v1/orders/), order listing, and detail views.
"""

from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from apps.inventory.models import Medicine

from .models import Order, OrderItem


class OrderItemInputSerializer(serializers.Serializer):
    """Validates a single line item submitted to the checkout endpoint."""

    medicine_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    """Read serializer for an OrderItem, including the medicine name."""

    medicine_name = serializers.CharField(source="medicine.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "medicine_id", "medicine_name", "quantity", "unit_price")


class OrderSerializer(serializers.ModelSerializer):
    """Read serializer for an Order, including nested line items."""

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "submitted_at", "total_amount", "items")


class CheckoutSerializer(serializers.Serializer):
    """
    Write serializer for the checkout endpoint (POST /api/v1/orders/).

    Validates the items list, looks up each medicine, captures the current
    unit_price, computes total_amount, and persists Order + OrderItems.
    """

    items = serializers.ListField(
        child=OrderItemInputSerializer(),
        min_length=1,
        error_messages={
            "min_length": "items must not be empty.",
            "required": "items is required.",
        },
    )

    def validate_items(self, items):
        """Ensure all referenced medicines exist."""
        medicine_ids = [item["medicine_id"] for item in items]
        found = set(
            Medicine.objects.filter(id__in=medicine_ids).values_list("id", flat=True)
        )
        missing = set(medicine_ids) - found
        if missing:
            raise serializers.ValidationError(
                f"Medicine IDs not found: {sorted(missing)}"
            )
        return items

    def create(self, validated_data):
        """
        Persist Order + OrderItems atomically.

        - unit_price is captured from Medicine.unit_price at the time of order.
        - total_amount is the sum of quantity × unit_price across all items.
        """
        farmer = self.context["request"].user
        items_data = validated_data["items"]

        # Fetch all medicines in one query
        medicine_ids = [item["medicine_id"] for item in items_data]
        medicines = {m.id: m for m in Medicine.objects.filter(id__in=medicine_ids)}

        # Compute total amount
        total_amount = Decimal("0.00")
        for item in items_data:
            medicine = medicines[item["medicine_id"]]
            total_amount += medicine.unit_price * item["quantity"]

        # Persist the order and line items atomically so a partial write never
        # leaves the database in an inconsistent state.
        with transaction.atomic():
            order = Order.objects.create(farmer=farmer, total_amount=total_amount)

            # Persist each line item with the unit price captured at order time
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    medicine=medicines[item["medicine_id"]],
                    quantity=item["quantity"],
                    unit_price=medicines[item["medicine_id"]].unit_price,
                )
                for item in items_data
            ])

        return order
