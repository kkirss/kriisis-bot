from .Command import Command


class EnableCommand(Command):
    COMMAND_STR = "enable"
    DESCRIPTION = "Enable notifications"

    PASS_ARGS = False

    @staticmethod
    def handle(bot, update):
        profile = bot.get_profile(update)
        if profile.telegram_notifications:
            bot.send_message(profile.telegram_chat_id, "You already have notifications enabled")
        else:
            profile.telegram_notifications = True
            profile.save()
            bot.send_message(profile.telegram_chat_id, "You have enabled notifications")


class DisableCommand(Command):
    COMMAND_STR = "disable"
    DESCRIPTION = "Disable notifications"

    PASS_ARGS = False

    @staticmethod
    def handle(bot, update):
        profile = bot.get_profile(update)
        if not profile.telegram_notifications:
            bot.send_message(profile.telegram_chat_id, "You already have notifications disabled")
        else:
            profile.telegram_notifications = False
            profile.save()
            bot.send_message(profile.telegram_chat_id, "You have disabled notifications")
