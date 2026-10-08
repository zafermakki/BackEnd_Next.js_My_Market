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
        "items/update/<int:item_id>/",
        CartItemUpdateView.as_view(),
        name="cart-item-update",
    ),

    # Delete cart item
    path(
        "items/delete/<int:item_id>/",
        CartItemDeleteView.as_view(),
        name="cart-item-delete",
    ),
]