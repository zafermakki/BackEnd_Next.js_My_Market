from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer

from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "quantity",
            "subtotal",
            "created_at",
            "updated_at",
        ]

    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "total",
            "created_at",
            "updated_at",
        ]

    def get_total(self, obj):
        return sum(
            item.product.price * item.quantity
            for item in obj.items.all()
        )


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(
        min_value=1,
        default=1
    )

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Product does not exist."
            )

        return value

class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(
        min_value=1
    )