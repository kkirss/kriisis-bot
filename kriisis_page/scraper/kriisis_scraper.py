import logging
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.db import transaction

from .models import Category, Discount, Shop


class KriisisScraper:
    BASE_URL = "http://www.kriisis.ee"
    DISCOUNT_URL = BASE_URL + "/allahindlus"
    CATEGORY_URL = BASE_URL + "/view_cat.php"
    ALL_SHOPS_URL = BASE_URL + "/allahindlus_poodides"
    ALL_CATEGORIES_URL = BASE_URL + "/allahindlus_kaubale"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.requests_session = requests.Session()

    def scrape_discount(self, discount_id, category):
        page = self.requests_session.get(KriisisScraper.DISCOUNT_URL, params={"id": discount_id})
        soup = BeautifulSoup(page.content, "html.parser")
        if len(soup.find_all("meta", content="0; URL=/")) > 0:
            self.logger.error("INVALID discount found (meta), {}".format(discount_id))
            raise RuntimeError
        if len(soup.find_all("finish")) > 0:
            self.logger.error("INVALID discount found (finish), {}".format(discount_id))
            raise RuntimeError

        discount = Discount(kriisis_id=discount_id, category=category)
        shop_names = soup.find("p", "big").text.split(": ")[1].split(", ")
        # discount.shops = session.query(Shop).filter(Shop.name.in_(shop_names)).all()
        shops = Shop.objects.query(name__in=shop_names)
        discount.shops.add(*shops)
        view_sale_dates = soup.find_all("p", "view_sale_date")
        discount.price = float(view_sale_dates[1].text.split(" ")[1][:-1])
        discount.item_name = view_sale_dates[1].find_next_sibling().contents[0].text
        try:
            discount.item_description = view_sale_dates[1].find_next_sibling().contents[1].text
        except IndexError:
            discount.item_description = ""
        period_text_split = view_sale_dates[0].text.split(" ")
        discount.start_date = datetime.strptime(period_text_split[2], "%d.%m.%Y").date()
        try:
            discount.end_date = datetime.strptime(period_text_split[4], "%d.%m.%Y").date()
        except IndexError:  # One day discount
            discount.end_date = discount.start_date
        discount.image_url = soup.find("img", class_=["img_big", "img_big2"]).get("src")
        discount.save()
        return discount

    def scrape_category(self, category):
        cat_type = int(str(category.kriisis_id)[0])
        cat_num = int(str(category.kriisis_id)[1:])
        if cat_type == 1:
            payload = {"cat": cat_num, "sort": 1, "page": 1}
        else:
            payload = {"cat2": cat_num, "sort": 1, "page": 1}
        found_discounts = []
        while 1:
            page = self.requests_session.get(KriisisScraper.CATEGORY_URL, params=payload)
            soup = BeautifulSoup(page.content, "html.parser")
            for sale_table_item in soup.find_all("table", class_="sale_table"):
                discount_id = int(sale_table_item.find("a").get("href").split("=")[-1])
                discount_exists = Discount.objects.filter(kriisis_id=discount_id).exists()
                # discount_exists = session.query(exists().where(Discount.kriisis_id == discount_id)).scalar()
                if not discount_exists:
                    found_discounts.append(self.scrape_discount(discount_id, category))
            if len(soup.find_all("div", class_="pstrnav")) < 2:  # Only one page
                break
            if soup.find_all("div", class_="pstrnav")[1].find_all("b")[-1].text != ">>":  # Last page
                break
            payload["page"] += 1
        return found_discounts

    def scrape_all_categories(self):
        self.logger.info("Starting discount scraping...")
        start_time = time.time()
        new_discounts = []
        end_categories = Category.objects.filter(children=None)
        for category in end_categories:
            self.logger.debug("Scraping category {}: {}".format(category.kriisis_id, category.name))
            found_discounts = self.scrape_category(category.category_id)
            new_discounts.extend(found_discounts)
        time_taken = time.time() - start_time
        self.logger.info(
            "Discount scraping took {:.3f} seconds, found {} discounts".format(time_taken, len(new_discounts)))
        return new_discounts

    def scrape_discounts(self):
        with transaction.atomic():
            new_discounts = self.scrape_all_categories()
        return new_discounts

    @staticmethod
    def scrape_categories():
        page = requests.get(KriisisScraper.ALL_CATEGORIES_URL)
        soup = BeautifulSoup(page.content, "html.parser")
        _, groceries_sfmenu, goods_sfmenu = soup.find_all("ul", class_="sf-menu")
        categories = {}  # category_id: Category
        for sfmenu in groceries_sfmenu, goods_sfmenu:
            # Prefixing the ids will keep groceries and goods ids unique
            if sfmenu == groceries_sfmenu:
                id_prefix = "1"
            else:
                id_prefix = "2"
            for li in sfmenu.find_all("li"):
                a = li.find("a")
                name = a.text.lstrip(">").split(" (")[0]
                category_id = int(id_prefix + a.get("href").split("=")[1])
                if category_id not in categories:
                    categories[category_id] = Category(kriisis_id=category_id, name=name)
                parent_li = li.parent.parent
                if parent_li.name == "li":  # Category has a parent category
                    parent_id = int(id_prefix + parent_li.find("a").get("href").split("=")[1])
                    parent_category = categories[parent_id]
                    categories[category_id].parents.add(parent_category)
        return categories.values()

    @staticmethod
    def scrape_shops():
        shops = []
        page = requests.get(KriisisScraper.ALL_SHOPS_URL)
        soup = BeautifulSoup(page.content, "html.parser")
        p_list = soup.find_all("p", class_=["shop", "shop_mx"])
        for p in p_list:
            name = p.text
            a = p.parent.find("a")
            image_url = KriisisScraper.BASE_URL + "/" + a.find("img").get("src")
            # This is necessary to get the shop_id because it's not in the shop list HTML
            shop_url = KriisisScraper.BASE_URL + "/" + a.get("href")
            shop_soup = BeautifulSoup(requests.get(shop_url).content, "html.parser")
            if len(shop_soup.find_all("p", class_="no_sale")) > 0:  # No discounts available for that shop
                continue
            shop_id = int(shop_soup.find("div", class_="pstrnav").find_all("a")[-1].get("href").split("=")[-1])
            shops.append(Shop(shop_id=shop_id, name=name, image_url=image_url))
        return shops
