import datetime
import logging

import telegram
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

from scraper.models import Category, Shop, Discount
from accounts.models import Profile


class KriisisBot(telegram.Bot):
    GITHUB_LINK = "https://github.com/runekri3/kriisis-bot"
    POLL_INTERVAL = 2
    SCRAPE_INTERVAL = 3600

    # TODO: Implement kampaaniad

    def __init__(self, scraper):
        super().__init__(settings.TELEGRAM_AUTH_TOKEN)
        self.logger = logging.getLogger(__name__)
        self.scraper = scraper
        self.updater = Updater(bot=self)
        self.add_handlers()

    def add_handlers(self):
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("help", self.__class__.help_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("start", self.__class__.start_command))
        dispatcher.add_handler(CommandHandler("enable", self.__class__.enable_command))
        dispatcher.add_handler(CommandHandler("disable", self.__class__.disable_command))
        dispatcher.add_handler(CommandHandler("add", self.__class__.add_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("remove", self.__class__.remove_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("addshop", self.__class__.addshop_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("addcategory", self.__class__.addcategory_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("removeshop", self.__class__.removeshop_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("removecategory", self.__class__.removecategory_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("github", self.__class__.github_command))
        dispatcher.add_handler(CommandHandler("shops", self.__class__.shops_command))
        # dispatcher.add_handler(CommandHandler("find", self.__class__.find_command, pass_args=True))

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

    def notify_user(self, profile, discount):  # TODO: Implement notifying the user
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

    def help_command(self, update, args=()):
        # TODO: Implement general help
        # TODO: Implement help for specific commands
        chat_id = update.message.chat_id
        self.send_message(chat_id, "Sorry but I can't help you because my dev is lazy")

    def start_command(self, update):
        user_id, chat_id = update.message.from_user.id, update.message.chat_id
        try:
            profile = Profile.objects.get(telegram_user_id=user_id)
        except ObjectDoesNotExist:
            profile = Profile(telegram_user_id=user_id, telegram_chat_id=chat_id)
            profile.save()
            self.send_message(chat_id, "Hello :)")
            self.help_command(update)
        else:
            self.send_message(chat_id, "You have already used /start. Use /help if you want help.")

    def enable_command(self, update):
        profile = self.get_profile(update)
        if profile.telegram_notifications:
            self.send_message(profile.telegram_chat_id, "You already have notifications enabled")
        else:
            profile.telegram_notifications = True
            profile.save()
            self.send_message(profile.telegram_chat_id, "You have enabled notifications")

    def disable_command(self, update):
        profile = self.get_profile(update)
        if not profile.telegram_notifications:
            self.send_message(profile.telegram_chat_id, "You already have notifications disabled")
        else:
            profile.telegram_notifications = False
            profile.save()
            self.send_message(profile.telegram_chat_id, "You have disabled notifications")

    def add_command(self, update, args, type_=None, remove=False):
        found_objects = []
        profile = self.get_profile(update)
        search_query = " ".join(args)
        try:
            obj_id = int(search_query)
        except ValueError:
            if type_ is Shop or type_ is None:
                found_objects.extend(list(Shop.objects.filter(name__icontains=search_query).all()))
            if type_ is Category or type_ is None:
                found_objects.extend(list(Category.objects.filter(name__icontains=search_query).all()))
            if not found_objects:
                self.send_message(profile.telegram_chat_id, "Found nothing with that name.")
                return
        else:
            if type_ is Shop or type_ is None:
                found_objects.extend(list(Shop.objects.filter(kriisis_id=obj_id).all()))
            if type_ is Category or type_ is None:
                found_objects.extend(list(Category.objects.filter(kriisis_id=obj_id).all()))
            if not found_objects:
                self.send_message(profile.telegram_chat_id, "Found nothing with that id.")
                return
        applicable_objects = []
        for found_object in found_objects:
            if type(found_object) is Shop:
                if remove:
                    applicable = found_object in profile.subscribed_shops.all()
                else:
                    applicable = found_object not in profile.subscribed_shops.all()
            elif type(found_object) is Category:
                if remove:
                    applicable = found_object in profile.subscribed_categories.all()
                else:
                    applicable = all(category not in profile.subscribed_categories.all() for category in
                                     [found_object] + list(found_object.ancestors))
            else:
                raise NotImplementedError("Unknown object found in add_command")
            if applicable:
                applicable_objects.append(found_object)
        if len(applicable_objects) == 0:
            if remove:
                if len(found_objects) == 1:
                    self.send_message(profile.telegram_chat_id, "You aren't subscribed to it.")
                else:
                    self.send_message(profile.telegram_chat_id, "You aren't subscribed to them.")
            else:
                if len(found_objects) == 1:
                    self.send_message(profile.telegram_chat_id, "You already are subscribed to it.")
                else:
                    self.send_message(profile.telegram_chat_id, "You already are subscribed to them.")
        elif len(applicable_objects) == 1:
            applicable_object = applicable_objects[0]
            if type(applicable_object) is Shop:
                if remove:
                    profile.subscribed_shops.remove(applicable_object)
                else:
                    profile.subscribed_shops.add(applicable_object)
            elif type(applicable_object) is Category:
                if remove:
                    profile.subscribed_categories.remove(applicable_object)
                else:
                    profile.subscribed_categories.add(applicable_object)
            else:
                raise NotImplementedError("Unknown object found in add_command")
            profile.save()
            if remove:
                self.send_message(profile.telegram_chat_id, "You removed {}.".format(str(applicable_object)))
            else:
                self.send_message(profile.telegram_chat_id, "You subscribed to {}.".format(str(applicable_object)))
        else:
            message = "Multiple matches found, please be more specific or use the id:"
            for applicable_object in applicable_objects:
                message += "\n" + str(applicable_object)
            self.send_message(profile.telegram_chat_id, message)

    def remove_command(self, update, args, type_=None):
        self.add_command(update, args, type_=type_, remove=True)

    def addshop_command(self, update, args):
        self.add_command(update, args, type_=Shop)

    def addcategory_command(self, update, args):
        self.add_command(update, args, type_=Category)

    def removeshop_command(self, update, args):
        self.remove_command(update, args, type_=Shop)

    def removecategory_command(self, update, args):
        self.remove_command(update, args, type_=Category)

    def github_command(self, update):
        chat_id = update.message.chat_id
        self.send_message(chat_id, self.GITHUB_LINK)

    def shops_command(self, update):
        profile = self.get_profile(update)
        message = "All shops:"
        for shop in Shop.objects.order_by("kriisis_id").all():
            message += "\n{shop.kriisis_id}: {shop.name}".format(shop=shop)
            if shop in profile.subscribed_shops.all():
                message += " (added)"
        self.send_message(profile.telegram_chat_id, message)

        # def find_command(self, update, args):
        #     max_categories = 20
        #     chat_id, user_id = update.message.chat_id, update.message.from_user.id
        #     search_query = " ".join(args).lower()
        #     found_categories = Category2.find_categories(search_query, max_categories)
        #     if not found_categories:
        #         self.send_message(chat_id, "Didn't find any categories. (for '{}')".format(search_query))
        #     else:
        #         message = "Found categories:"
        #         for category in found_categories:
        #             message += "\n" + str(category)
        #         if len(found_categories) == max_categories:
        #             message += "\nThere may be more categories, try a more specific term."
        #         self.send_message(chat_id, message)
