from django.db import models
from hashid_field import HashidAutoField


class Category(models.Model):
    """A category of some product/service"""
    id = HashidAutoField(primary_key=True)
    kriisis_id = models.IntegerField(unique=True)

    name = models.TextField()
    children = models.ManyToManyField("scraper.Category", related_name="parents", blank=True)
    subscribed_users = models.ManyToManyField("accounts.User", related_name="subscribed_categories")


class Shop(models.Model):
    """A retail shop"""
    id = HashidAutoField(primary_key=True)
    kriisis_id = models.IntegerField(unique=True)

    name = models.TextField()
    image_url = models.TextField()

    subscribed_users = models.ManyToManyField("accounts.User", related_name="subscribed_shops")


class Discount(models.Model):
    """A discount on some product/service"""
    id = HashidAutoField(primary_key=True)
    kriisis_id = models.IntegerField(unique=True)

    item_name = models.TextField('item name')
    item_description = models.TextField('item description')
    price = models.FloatField()
    image_url = models.TextField('image url')
    telegram_image_file_id = models.TextField('telegram image file id', blank=True)
    start_date = models.DateField('start date')
    end_date = models.DateField('end date')

    shops = models.ManyToManyField(Shop, related_name="discounts")
    category = models.ForeignKey(Category, related_name="discounts", on_delete=models.CASCADE)
