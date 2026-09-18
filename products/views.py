from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

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
            queryset = queryset.filter(
                category_id=category_id
        )

        search_query = self.request.query_params.get("search")

        if search_query:
            queryset = queryset.filter(
                name__icontains=search_query
            )
        return queryset
