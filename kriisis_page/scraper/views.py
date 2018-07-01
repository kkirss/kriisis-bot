from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets, mixins

from .models import Category, Shop, Discount
from .serializers import CategorySerializer, ShopSerializer, DiscountSerializer


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    lookup_field = "id"

    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)
    filter_fields = ("name",)
    search_fields = ("name",)
    ordering_fields = ("name",)


class ShopViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    lookup_field = "id"

    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)
    filter_fields = ("name",)
    search_fields = ("name",)
    ordering_fields = ("name",)


class DiscountViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

    lookup_field = "id"

    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)
    filter_fields = ("price", "start_date", "end_date",
                     "category", "shops")
    search_fields = ("item_name", "item_description")
    ordering_fields = ("item_name", "item_description",
                       "start_date", "end_date",
                       "price")
    ordering = ("start_date",)
