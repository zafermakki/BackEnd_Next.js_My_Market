from rest_framework import generics
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.permissions import AllowAny

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = (
            Product.objects
            .all()
            .select_related("category")
            .prefetch_related("images")
        )

        category_id = self.request.query_params.get("category")

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset
