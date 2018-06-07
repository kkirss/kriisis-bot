from scraper.models import Shop, Category
from .Command import Command


class HelpCommand(Command):
    COMMAND_STR = "help"
    DESCRIPTION = "Gives help"

    PASS_ARGS = False

    ALL_COMMANDS = ()

    @staticmethod
    def handle(bot, update):
        # TODO: Implement help for specific commands
        chat_id = update.message.chat_id
        help_texts = [command.get_help_text() for command in bot.ALL_COMMANDS]
        message = "\n".join(help_texts)
        bot.send_message(chat_id, message)


class GithubCommand(Command):
    COMMAND_STR = "github"
    DESCRIPTION = "Link Github repo"

    PASS_ARGS = False

    @staticmethod
    def handle(bot, update):
        chat_id = update.message.chat_id
        bot.send_message(chat_id, bot.GITHUB_LINK)


class ShopsCommand(Command):
    COMMAND_STR = "shops"
    DESCRIPTION = "List all shops"

    PASS_ARGS = False

    @staticmethod
    def handle(bot, update):
        profile = bot.get_profile(update)
        message = "All shops:"
        for shop in Shop.objects.order_by("kriisis_id").all():
            message += "\n{}".format(shop.long_name)
            if shop in profile.subscribed_shops.all():
                message += " (added)"
        bot.send_message(profile.telegram_chat_id, message)


class FindCategoryCommand(Command):
    COMMAND_STR = "findcategory"
    DESCRIPTION = "Find categories with keyword(s)"

    PASS_ARGS = True

    @staticmethod
    def handle(bot, update, args):
        max_categories = 20
        chat_id, user_id = update.message.chat_id, update.message.from_user.id
        search_query = " ".join(args).lower()
        found_categories = Category.objects.filter(name__icontains=search_query)
        if not found_categories.exists():
            bot.send_message(chat_id, "Didn't find any categories. (for '{}')".format(search_query))
        else:
            message = "Found categories:"
            for category in found_categories.all():
                message += "\n" + category.long_name
            if len(found_categories) == max_categories:
                message += "\nThere may be more categories, try a more specific term."
            bot.send_message(chat_id, message)
