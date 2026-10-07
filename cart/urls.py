from django.urls import path

from .views import (
    CartItemCreateView,
    CartItemDeleteView,
    CartItemUpdateView,
    CartView,
)

urlpatterns = [
    # View current user's cart
    path(
        "",
        CartView.as_view(),
        name="cart-detail",
    ),

    # Add product to cart
    path(
        "items/",
        CartItemCreateView.as_view(),
        name="cart-item-add",
    ),

    # Update cart item quantity
    path(
        "items/<int:item_id>/update",
        CartItemUpdateView.as_view(),
        name="cart-item-update",
    ),

    # Delete cart item
    path(
        "items/<int:item_id>/delete",
        CartItemDeleteView.as_view(),
        name="cart-item-delete",
    ),
]