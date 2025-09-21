import telegram

from abh.src.consts import GeomagStormIndex
from abh.src.consts import SolarFlareClass
from abh.src.scrapers.scraper import ScrapeResult


# --
# Classes
# --

class ChatSettings():

    def __init__(self):
        self.active_intensity_alert: ScrapeResult | None = None
        self.active_flare_alert: ScrapeResult | None = None
        self._send_updates = True
        self._include_data = True
        self._include_images = True
        self._predict_time = True
        self._northern_hemisphere = True
        self._southern_hemisphere = True
        self._min_flare_class = SolarFlareClass.X1
        self._min_geomag_value = GeomagStormIndex.KP7

    # end def

    @property
    def send_updates(self) -> bool:
        return self._send_updates

    # end def

    @send_updates.setter
    def send_updates(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError("Value must be of bool type")
        # end if
        self._send_updates = value

    # end def

    @property
    def include_data(self) -> bool:
        return self._include_data

    # end def

    @include_data.setter
    def include_data(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError("Value must be of bool type")
        # end if
        self._include_data = value

    # end def

    @property
    def include_images(self) -> bool:
        return self._include_images

    # end def

    @include_images.setter
    def include_images(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError("Value must be of bool type")
        # end if
        self._include_images = value

    # end def

    @property
    def predict_time(self) -> bool:
        return self._predict_time

    # end def

    @predict_time.setter
    def predict_time(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError("Value must be of bool type")
        # end if
        self._predict_time = value

    # end def

    @property
    def northern_hemisphere(self) -> bool:
        return self._northern_hemisphere

    # end def

    @northern_hemisphere.setter
    def northern_hemisphere(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError("Value must be of bool type")
        # end if
        self._northern_hemisphere = value

    # end def

    @property
    def southern_hemisphere(self) -> bool:
        return self._southern_hemisphere

    # end def

    @southern_hemisphere.setter
    def southern_hemisphere(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError("Value must be of bool type")
        # end if
        self._southern_hemisphere = value

    # end def

    @property
    def min_flare_class(self) -> SolarFlareClass:
        return self._min_flare_class

    # end def

    @min_flare_class.setter
    def min_flare_class(self, value: SolarFlareClass):
        if not isinstance(value, SolarFlareClass):
            raise ValueError("Value must be of SolarFlareClass type")
        # end if
        self._min_flare_class = value

    # end def

    @property
    def min_geomag_value(self) -> GeomagStormIndex:
        return self._min_geomag_value

    # end def

    @min_geomag_value.setter
    def min_geomag_value(self, value: GeomagStormIndex):
        if not isinstance(value, GeomagStormIndex):
            raise ValueError("Value must be of GeomagStormIndex type")
        # end if
        self._min_geomag_value = value
    # end def


# end class


class Chat():

    def __init__(self, uid: int, admins: list[int]):
        self._settings = ChatSettings()
        self._uid = uid
        self._admins = admins

    # end def

    def is_admin(self, uid: int) -> bool:
        return uid in self._admins

    # end def

    def update_admins(self, admins: tuple):
        admin_ids = []
        # Get everyone's ID
        for admin in admins:
            # Single user
            if isinstance(admin, telegram.Chat):
                user: telegram.User = admin
            else:
                user: telegram.User = admin.user
            # end if
            admin_ids.append(user.id)
        # end for
        self._admins = admin_ids

    # end def

    @property
    def settings(self) -> ChatSettings:
        return self._settings

    # end def

    @property
    def uid(self) -> int:
        return self._uid

    # end def

    @property
    def admins(self) -> list[int]:
        return self._admins[:]
    # end def
# end class
