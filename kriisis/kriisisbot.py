import datetime
import logging
import time

import telegram
from sqlalchemy import exists
from sqlalchemy import inspect
from telegram.ext import Job
from telegram.ext import Updater, CommandHandler

from .models import Category, Shop, User


class KriisisBot(telegram.Bot):
    GITHUB_LINK = ""  # TODO: Upload to github
    AUTH_TOKEN_LOCATION = "Telegram Auth Token.txt"  # TODO: Perhaps a more elegant solution down the line
    POLL_INTERVAL = 2
    SCRAPE_INTERVAL = 3600

    # TODO: Implement getting notifications at specific hours
    # TODO: Implement kampaaniad
    # TODO: Implement sending pictures

    def __init__(self, session_factory, scraper):
        with open(self.AUTH_TOKEN_LOCATION) as f:
            token = f.readline().strip()
        super().__init__(token)
        self.logger = logging.getLogger(__name__)
        self.session_factory = session_factory
        self.scraper = scraper
        self.updater = Updater(bot=self)
        self.add_handlers()
        self.scrape_job = Job(self.__class__.scrape, self.SCRAPE_INTERVAL)
        self.hourly_notify_job = Job(self.__class__.hourly_notify, 3600)

    def add_handlers(self):
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("help", self.__class__.help_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("start", self.__class__.start_command))
        dispatcher.add_handler(CommandHandler("add", self.__class__.add_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("remove", self.__class__.remove_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("addshop", self.__class__.addshop_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("addcategory", self.__class__.addcategory_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("removeshop", self.__class__.removeshop_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("removecategory", self.__class__.removecategory_command, pass_args=True))
        dispatcher.add_handler(CommandHandler("github", self.__class__.github_command))
        # dispatcher.add_handler(CommandHandler("shops", self.__class__.shops_command, pass_args=True))
        # dispatcher.add_handler(CommandHandler("find", self.__class__.find_command, pass_args=True))

    def start_bot(self):
        now = datetime.datetime.now()
        self.updater.job_queue.run_repeating(self.__class__.hourly_notify, name="Hourly notify Job", interval=3600, first=0)
        self.updater.job_queue.run_repeating(self.__class__.scrape, name="Scrape Job", interval=600, first=0)
        self.updater.start_polling(poll_interval=self.POLL_INTERVAL)
    
    def send_message(self, chat_id, text, *args, **kwargs):
        try:
            resp = super().send_message(chat_id, text, *args, **kwargs)
        except telegram.error.BadRequest as e:
            if "chat not found" in e.message:
                self.logger.info("Chat not found for chat_id", chat_id, "Deleting the user")
                session = self.session_factory()
                user = session.query(User).filter_by(chat_id=chat_id).first()
                session.delete(user)
                session.commit()
    
    def process_new_discounts(self, new_discounts):
        self.logger.info("Processing new discounts...")
        # TODO: Implement processing new discounts
        session = self.session_factory()
        for discount in new_discounts:
            shop_ids = [shop.shop_id for shop in discount.shops]
            users = session.query(User).filter(User.subscribed_categories.contains(discount.category))
            users.filter(User.subscribed_shops.any(Shop.shop_id.in_(shop_ids)))
            for user in users.all():
                self.notify_user(user, discount)
                time.sleep(1)
        self.logger.info("Processing complete")

    def notify_user(self, user, discount):  # TODO: Implement notifying the user
        self.logger.debug("NOTIFYING USER ", user.user_id)
        if user.picture_notifications:
            if discount.image_file_id is not None:
                self.send_photo(user.chat_id, discount.image_file_id)
            else:
                message = self.send_photo(user.chat_id, discount.image_url)
                discount.image_file_id = message.photo[0].file_id
                inspect(discount).session.commit()
        self.send_message(user.chat_id, discount.notification_str)

    def scrape(self, job):
        new_discounts = self.scraper.scrape_discounts()
        if len(new_discounts) > 0:
            self.process_new_discounts(new_discounts)

    def hourly_notify(self, job):  # TODO: Implement hourly notifications
        cur_hour = datetime.datetime.now().hour
        self.logger.info("Hourly ({}) check for discounts to notify...".format(cur_hour))

    def get_user(self, update, session):
        user = session.query(User).get(update.message.from_user.id)
        if user is None:
            self.send_message(update.message.chat_id, "Please use /start first.")
            raise RuntimeError("User hadn't used /start")
        else:
            return user

    def help_command(self, update, args=()):
        # TODO: Implement general help
        # TODO: Implement help for specific commands
        chat_id = update.message.chat_id
        self.send_message(chat_id, "Sorry but I can't help you because my dev is lazy")

    def start_command(self, update):
        user_id, chat_id = update.message.from_user.id, update.message.chat_id
        session = self.session_factory()
        if session.query(exists().where(User.user_id == user_id)).scalar():
            self.send_message(chat_id, "You have already used /start. Use /help if you want help.")
        else:
            session.add(User(user_id=user_id, chat_id=chat_id))
            session.commit()
            self.send_message(chat_id, "Hello :)")
            self.help_command(update)

    def add_command(self, update, args, type_=None, remove=False):
        found_objects = []
        session = self.session_factory()
        user = self.get_user(update, session)
        search_query = " ".join(args)
        try:
            obj_id = int(search_query)
        except ValueError:
            if type_ is Shop or type_ is None:
                found_objects.extend(Shop.search(search_query, session))
            if type_ is Category or type_ is None:
                found_objects.extend(Category.search(search_query, session))
            if not found_objects:
                self.send_message(user.chat_id, "Found nothing with that name.")
                return
        else:
            if type_ is Shop or type_ is None:
                found_objects.extend(session.query(Shop).filter(Shop.shop_id == obj_id).limit(1).all())
            if type_ is Category or type_ is None:
                found_objects.extend(session.query(Category).filter(Category.category_id == obj_id).limit(1).all())
            if not found_objects:
                self.send_message(user.chat_id, "Found nothing with that id.")
                return
        applicable_objects = []
        for found_object in found_objects:
            if type(found_object) is Shop:
                if remove:
                    applicable = found_object in user.subscribed_shops
                else:
                    applicable = found_object not in user.subscribed_shops
            elif type(found_object) is Category:
                if remove:
                    applicable = found_object in user.subscribed_categories
                else:
                    applicable = all(category not in user.subscribed_categories for category in
                                     [found_object] + list(found_object.ancestors))
            else:
                raise NotImplementedError("Unknown object found in add_command")
            if applicable:
                applicable_objects.append(found_object)
        if len(applicable_objects) == 0:
            if remove:
                if len(found_objects) == 1:
                    self.send_message(user.chat_id, "You aren't subscribed to it.")
                else:
                    self.send_message(user.chat_id, "You aren't subscribed to them.")
            else:
                if len(found_objects) == 1:
                    self.send_message(user.chat_id, "You already are subscribed to it.")
                else:
                    self.send_message(user.chat_id, "You already are subscribed to them.")
        elif len(applicable_objects) == 1:
            applicable_object = applicable_objects[0]
            if type(applicable_object) is Shop:
                user.subscribed_shops.append(applicable_object)
            elif type(applicable_object) is Category:
                user.subscribed_categories.append(applicable_object)
            else:
                raise NotImplementedError("Unknown object found in add_command")
            session.commit()
            if remove:
                self.send_message(user.chat_id, "You removed {}.".format(str(applicable_object)))
            else:
                self.send_message(user.chat_id, "You subscribed to {}.".format(str(applicable_object)))
        else:
            message = "Multiple matches found, please be more specific or use the id:"
            for applicable_object in applicable_objects:
                message += "\n" + str(applicable_object)
            self.send_message(user.chat_id, message)

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

        # def shops_command(self, update):
        #     chat_id, user_id = update.message.chat_id, update.message.from_user.id
        #     user = self.database.get_user(user_id)
        #     message = "All shops:"
        #     for shop in Shop2.get_all_shops():
        #         message += "\n" + str(shop.shop_id) + ": " + shop.name
        #         if user.has_shop():
        #             message += " (added)"
        #     self.send_message(chat_id, message)
        #
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
