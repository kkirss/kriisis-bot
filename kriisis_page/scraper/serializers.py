from hashid_field.rest import HashidSerializerCharField
from rest_framework import serializers

from .models import Category, Shop, Discount


class SlimCategorySerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name")
        read_only_fields = ("id", "name")


class CategorySerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)
    children = SlimCategorySerializer(read_only=True)
    parents = SlimCategorySerializer(read_only=True)

    class Meta:
        model = Category
        fields = ("id", "kriisis_id", "name", "children", "parents")
        read_only_fields = ("id", "kriisis_id", "name", 'children', "parents")


class SlimShopSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)

    class Meta:
        model = Shop
        fields = ("id", "name")
        read_only_fields = ("id", "name")


class ShopSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)

    class Meta:
        model = Shop
        fields = ("id", "kriisis_id", "name", "image_url")
        read_only_fields = ("id", "kriisis_id", "name", "image_url")


class DiscountSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)
    shops = SlimShopSerializer(read_only=True, many=True)
    category = SlimCategorySerializer(read_only=True)

    class Meta:
        model = Discount
        fields = ("id", "kriisis_id", "item_name", "item_description",
                  "price", "image_url", "start_date", "end_date",
                  "shops", "category")
        read_only_fields = ("id", "kriisis_id", "item_name", "item_description",
                            "price", "image_url", "start_date", "end_date",
                            "shops", "category")
