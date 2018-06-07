import datetime
import logging

import telegram
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

from scraper.models import Discount
from accounts.models import Profile
from .commands import AddCommands, InfoCommands, SettingsCommands, StartCommand


class KriisisBot(telegram.Bot):
    GITHUB_LINK = "https://github.com/runekri3/kriisis-bot"
    POLL_INTERVAL = 2
    SCRAPE_INTERVAL = 3600

    ALL_COMMANDS = (
        AddCommands.AddCommand,
        AddCommands.RemoveCommand,
        AddCommands.AddCategoryCommand,
        AddCommands.AddShopCommand,
        AddCommands.RemoveCategoryCommand,
        AddCommands.RemoveShopCommand,
        InfoCommands.HelpCommand,
        InfoCommands.FindCategoryCommand,
        InfoCommands.GithubCommand,
        InfoCommands.ShopsCommand,
        SettingsCommands.EnableCommand,
        SettingsCommands.DisableCommand,
        StartCommand.StartCommand
    )

    # TODO: Implement kampaaniad

    def __init__(self, scraper):
        super().__init__(settings.TELEGRAM_AUTH_TOKEN)
        self.logger = logging.getLogger(__name__)
        self.scraper = scraper
        self.updater = Updater(bot=self)
        self.add_handlers()

    def add_handlers(self):
        dispatcher = self.updater.dispatcher
        for command in self.__class__.ALL_COMMANDS:
            dispatcher.add_handler(CommandHandler(command.COMMAND_STR, command.handle, pass_args=command.PASS_ARGS))

    def start_bot(self):
        now = datetime.datetime.now()
        next_hour = 3600 - (now - now.replace(minute=0, second=0)).total_seconds() + 1
        self.updater.job_queue.run_repeating(self.__class__.hourly_notify, name="Hourly notify Job", interval=3600, first=next_hour)
        self.updater.job_queue.run_repeating(self.__class__.scrape, name="Scrape Job", interval=600, first=0)
        self.updater.start_polling(poll_interval=self.POLL_INTERVAL)
    
    def send_message(self, chat_id, text, *args, **kwargs):
        try:
            resp = super().send_message(chat_id, text, *args, **kwargs)
        except telegram.error.BadRequest as e:
            if "chat not found" in e.message:
                self.logger.info("Chat not found for chat_id", chat_id, "Deleting the user")
                try:
                    profile = Profile.objects.get(telegram_chat_id=chat_id)
                except ObjectDoesNotExist:
                    pass
                else:
                    profile.delete()

    def send_notifications(self, hourly=False):
        profiles_to_notify = Profile.objects.filter(telegram_notifications=True)
        if hourly:
            cur_hour = datetime.datetime.now().hour
            profiles_to_notify = profiles_to_notify.filter(telegram_notification_hour=cur_hour)
        else:
            profiles_to_notify = profiles_to_notify.filter(telegram_notification_hour=None)
        for profile in profiles_to_notify.all():
            discounts = Discount.objects\
                .filter(kriisis_id__lt=profile.kriisis_last_discount_id)\
                .filter(category__in=profile.subscribed_categories)\
                .filter(shops__in=profile.subscribed_shops)
            for discount in discounts.all():
                self.notify_user(profile, discount)
                if discount.discount_id > profile.kriisis_last_discount_id:
                    profile.kriisis_last_discount_id = discount.discount_id
                    profile.save()
        self.logger.info("Processing complete")

    def notify_user(self, profile, discount):
        if profile.telegram_picture_notifications:
            if discount.image_file_id is not None:
                self.send_photo(profile.telegram_chat_id, discount.image_file_id)
            else:
                message = self.send_photo(profile.telegram_chat_id, discount.image_url)
                discount.image_file_id = message.photo[0].file_id
                discount.save()
        self.send_message(profile.telegram_chat_id, discount.notification_str, parse_mode=ParseMode.MARKDOWN)

    def scrape(self, job):
        new_discounts = self.scraper.scrape_discounts()
        if len(new_discounts) > 0:
            self.send_notifications()

    def hourly_notify(self, job):
        cur_hour = datetime.datetime.now().hour
        self.send_notifications(hourly=True)
        self.logger.info("Hourly ({}) check for discounts to notify...".format(cur_hour))

    def get_profile(self, update):
        try:
            profile = Profile.objects.get(telegram_user_id=update.message.from_user.id)
        except ObjectDoesNotExist:
            self.send_message(update.message.chat_id, "Please use /start first.")
            self.logger.debug("User hadn't used /start")
        else:
            return profile
