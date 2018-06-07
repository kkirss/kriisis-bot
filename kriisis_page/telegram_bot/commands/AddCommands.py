from scraper.models import Shop, Category
from .Command import Command


def add_command(bot, update, args, type_=None, remove=False):
    found_objects = []
    profile = bot.get_profile(update)
    search_query = " ".join(args)
    try:
        obj_id = int(search_query)
    except ValueError:
        if type_ is Shop or type_ is None:
            found_objects.extend(list(Shop.objects.filter(name__icontains=search_query).all()))
        if type_ is Category or type_ is None:
            found_objects.extend(list(Category.objects.filter(name__icontains=search_query).all()))
        if not found_objects:
            bot.send_message(profile.telegram_chat_id, "Found nothing with that name.")
            return
    else:
        if type_ is Shop or type_ is None:
            found_objects.extend(list(Shop.objects.filter(kriisis_id=obj_id).all()))
        if type_ is Category or type_ is None:
            found_objects.extend(list(Category.objects.filter(kriisis_id=obj_id).all()))
        if not found_objects:
            bot.send_message(profile.telegram_chat_id, "Found nothing with that id.")
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
                bot.send_message(profile.telegram_chat_id, "You aren't subscribed to it.")
            else:
                bot.send_message(profile.telegram_chat_id, "You aren't subscribed to them.")
        else:
            if len(found_objects) == 1:
                bot.send_message(profile.telegram_chat_id, "You already are subscribed to it.")
            else:
                bot.send_message(profile.telegram_chat_id, "You already are subscribed to them.")
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
            bot.send_message(profile.telegram_chat_id, "You removed {}.".format(str(applicable_object)))
        else:
            bot.send_message(profile.telegram_chat_id, "You subscribed to {}.".format(str(applicable_object)))
    else:
        message = "Multiple matches found, please be more specific or use the id:"
        for applicable_object in applicable_objects:
            message += "\n" + applicable_object.long_name
        bot.send_message(profile.telegram_chat_id, message)


class AddCommand(Command):
    COMMAND_STR = "add"
    DESCRIPTION = "Add a category or shop using name or id"

    PASS_ARGS = True

    @staticmethod
    def handle(bot, update, args):
        add_command(bot, update, args)


class RemoveCommand(Command):
    COMMAND_STR = "remove"
    DESCRIPTION = "Remove a category or shop using name or id"

    PASS_ARGS = True

    @staticmethod
    def handle(bot, update, args):
        add_command(bot, update, args, remove=True)


class AddShopCommand(Command):
    COMMAND_STR = "addshop"
    DESCRIPTION = "Add a shop using name or id"

    PASS_ARGS = True

    @staticmethod
    def handle(bot, update, args):
        add_command(bot, update, args, type_=Shop)


class AddCategoryCommand(Command):
    COMMAND_STR = "addcategory"
    DESCRIPTION = "Add a category using name or id"

    PASS_ARGS = True

    @staticmethod
    def handle(bot, update, args):
        add_command(bot, update, args, type_=Category)


class RemoveShopCommand(Command):
    COMMAND_STR = "removeshop"
    DESCRIPTION = "Remove a shop using name or id"

    PASS_ARGS = True

    @staticmethod
    def handle(bot, update, args):
        add_command(bot, update, args, type_=Shop, remove=True)


class RemoveCategoryCommand(Command):
    COMMAND_STR = "removecategory"
    DESCRIPTION = "Remove a category using name or id"

    PASS_ARGS = True

    @staticmethod
    def handle(bot, update, args):
        add_command(bot, update, args, type_=Category, remove=True)
