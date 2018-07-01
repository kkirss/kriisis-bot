from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'shops', views.ShopViewSet)
router.register(r'discounts', views.DiscountViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
]
