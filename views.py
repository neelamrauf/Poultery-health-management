"""
Orders views.

- OrderListCreateView:  POST /api/v1/orders/   — checkout (create order)
                        GET  /api/v1/orders/   — list farmer's orders
- OrderDetailView:      GET  /api/v1/orders/{id}/ — retrieve order with line items
"""

from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsFarmer

from .models import Order
from .serializers import CheckoutSerializer, OrderSerializer


class OrderListCreateView(APIView):
    """
    POST /api/v1/orders/
        Validate a non-empty cart, capture unit prices, persist Order +
        OrderItems, and return 201 with the order ID and success message.
        Requires: Farmer role.

    GET /api/v1/orders/
        Return the authenticated Farmer's orders ordered by submitted_at
        descending.
        Requires: Farmer role.
    """

    permission_classes = [IsFarmer]

    def post(self, request):
        serializer = CheckoutSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        return Response(
            {
                "id": order.id,
                "message": "Order placed successfully.",
                "total_amount": str(order.total_amount),
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        orders = (
            Order.objects.filter(farmer=request.user)
            .prefetch_related("items__medicine")
            .order_by("-submitted_at")
        )
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDetailView(RetrieveAPIView):
    """
    GET /api/v1/orders/{id}/
    Returns a single Order with its line items for the authenticated Farmer.
    Requires: Farmer role.
    """

    permission_classes = [IsFarmer]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            Order.objects.filter(farmer=self.request.user)
            .prefetch_related("items__medicine")
        )
