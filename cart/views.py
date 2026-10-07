from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import (
    AddToCartSerializer,
    CartItemSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
)


class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(
            user=self.request.user
        )

        return cart

class CartItemCreateView(generics.CreateAPIView):
    serializer_class = AddToCartSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        cart, _ = Cart.objects.get_or_create(
            user=request.user
        )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={
                "quantity": quantity
            }
        )

        # المنتج موجود مسبقاً في السلة
        if not created:
            cart_item.quantity += quantity
            cart_item.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

        response_serializer = CartItemSerializer(
            cart_item
        )

        return Response(
            response_serializer.data,
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            )
        )

class CartItemUpdateView(generics.UpdateAPIView):
    serializer_class = UpdateCartItemSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_object(self):
        return get_object_or_404(
            CartItem,
            id=self.kwargs["item_id"],
            cart__user=self.request.user,
        )

    def patch(self, request, *args, **kwargs):
        item = self.get_object()

        serializer = self.get_serializer(
            item,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        item.quantity = serializer.validated_data["quantity"]

        item.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        return Response(
            CartItemSerializer(item).data,
            status=status.HTTP_200_OK,
        )

class CartItemDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(
            CartItem,
            id=self.kwargs["item_id"],
            cart__user=self.request.user,
        )