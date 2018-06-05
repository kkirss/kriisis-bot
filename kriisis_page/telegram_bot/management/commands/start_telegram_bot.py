import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from scraper.kriisis_scraper import KriisisScraper
from scraper.models import Shop, Category
from telegram_bot.kriisis_bot import KriisisBot


class Command(BaseCommand):
    help = "Start the Telegram bot"
    logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.DEBUG)
        self.logger.info("Initializing telegram bot...")
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("telegram").setLevel(logging.INFO)
        logging.getLogger("JobQueue").setLevel(logging.INFO)
        logging.getLogger("telegram_bot.kriisis_bot").setLevel(logging.INFO)
        logging.getLogger("bs4").setLevel(logging.ERROR)
        if not Shop.objects.exists():
            self.logger.info("Scraping all shops and categories...")
            Shop.objects.all().delete()
            Category.objects.all().delete()
            with transaction.atomic():
                shops = KriisisScraper.scrape_shops()
                categories = KriisisScraper.scrape_categories()
        scraper = KriisisScraper()
        self.logger.info("Starting telegram bot...")
        kriisis_bot = KriisisBot(scraper)
        kriisis_bot.start_bot()
        self.logger.info("Started telegram bot")