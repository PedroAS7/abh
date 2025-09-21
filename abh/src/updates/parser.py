import telegram


class TelegramUpdateParser():

    def can_handle(self, update: telegram.Update) -> bool:
        return False

    # end def

    async def parse(self, update: telegram.Update, app: object):
        raise NotImplementedError("Parser did not implement parser")
    # end def
# end class
