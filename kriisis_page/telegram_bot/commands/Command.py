class Command:
    HELP_TEXT_FORMAT = "/{cmd.COMMAND_STR} - {cmd.DESCRIPTION}"

    COMMAND_STR = ""
    DESCRIPTION = ""

    PASS_ARGS = False

    @staticmethod
    def handle(*args, **kwargs):
        pass

    @classmethod
    def get_help_text(cls):
        return cls.HELP_TEXT_FORMAT.format(cmd=cls)
