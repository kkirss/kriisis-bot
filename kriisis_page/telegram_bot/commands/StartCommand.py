from accounts.models import Profile
from .Command import Command


class StartCommand(Command):
    COMMAND_STR = "start"
    DESCRIPTION = "Register"

    PASS_ARGS = False

    @staticmethod
    def handle(bot, update):
        user_id, chat_id = update.message.from_user.id, update.message.chat_id
        if Profile.objects.filter(telegram_user_id=user_id).exists():
            bot.send_message(chat_id, "You have already used /start. Use /help if you want help.")
        else:
            profile = Profile(telegram_user_id=user_id, telegram_chat_id=chat_id)
            profile.save()
            bot.send_message(chat_id, "Hello :)")
            bot.help_command(update)
