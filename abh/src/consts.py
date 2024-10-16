from enum import IntEnum
from enum import Enum
import math


#--
# Classes
#--

class ClassWithHelp():
    @staticmethod
    def get_help() -> dict[object, str]:
        raise NotImplementedError("Class did not implement help method")
    # end def
# end class


class SolarFlareClass(ClassWithHelp, IntEnum):
    # Class is 10 ^ (val / 10)
    OTHER = 0
    B1  = -70
    B5  = -65
    C1  = -60
    C5  = -55
    M1  = -50
    M5  = -45
    X1  = -40
    X5  = -35
    X10 = -30
    X20 = -20
    X30 = -10
    
    @staticmethod
    def get_help() -> dict[object, str]:
        # https://svs.gsfc.nasa.gov/10109/
        return {
            SolarFlareClass.OTHER: "Other class. Triggers every time",
            SolarFlareClass.B1:    "Weak. Will trigger a lot of alerts",
            SolarFlareClass.B5:    "Weak. Will trigger a lot of alerts",
            SolarFlareClass.C1:    "Weak. Will trigger a lot of alerts",
            SolarFlareClass.C5:    "Moderate. Will trigger a lot of alerts",
            SolarFlareClass.M1:    "Moderate. Will trigger a lot of alerts",
            SolarFlareClass.M5:    "Moderate (350 per solar cycle). Might trigger a lot of alerts",
            SolarFlareClass.X1:    "Strong (175 per solar cycle)",
            SolarFlareClass.X5:    "Very strong (75 per solar cycle)",
            SolarFlareClass.X10:   "Severe (8 per solar cycle)",
            SolarFlareClass.X20:   "Extreme (1 per solar cycle)",
            SolarFlareClass.X30:   "Unbelievably extreme (here as a placeholder for >X20)"
        }
    # end def

    @staticmethod
    def lowest() -> 'SolarFlareClass':
        return SolarFlareClass.B1
    # end def

    @staticmethod
    def highest() -> 'SolarFlareClass':
        return SolarFlareClass.X30
    # end def

    @staticmethod
    def round_to_val(value: float) -> 'SolarFlareClass':
        # Calculate corresponding class
        log10_intensity = math.log10(value)
        norm_intensity = math.floor(log10_intensity * 10)

        if norm_intensity < SolarFlareClass.lowest():
            flare_class = SolarFlareClass.OTHER
        elif norm_intensity > SolarFlareClass.highest():
            flare_class = SolarFlareClass.highest()
        else:
            mod = -norm_intensity % 5
            flare_class = SolarFlareClass(norm_intensity + mod)
        # end if

        return flare_class
    # end def
# end class


class GeomagStormIndex(ClassWithHelp, IntEnum):
    KP0 = 0,
    KP1 = 1,
    KP2 = 2,
    KP3 = 3,
    KP4 = 4,
    KP5 = 5,
    KP6 = 6,
    KP7 = 7,
    KP8 = 8,
    KP9 = 9
    
    @staticmethod
    def get_help() -> dict[object, str]:
        # https://auroraforecast.is/kp-index/
        # https://www.spaceweatherlive.com/en/help/the-kp-index.html
        return {
            GeomagStormIndex.KP0: "Faintly visible on very high latitudes (such as north of Iceland)",
            GeomagStormIndex.KP1: "Visible at Iceland",
            GeomagStormIndex.KP2: "Bright at Iceland",
            GeomagStormIndex.KP3: "Visible from northern Europe",
            GeomagStormIndex.KP4: "Bright on northern European countries",
            GeomagStormIndex.KP5: "Bright at Scotland and southern Sweden",
            GeomagStormIndex.KP6: "Bright at countries at Denmark",
            GeomagStormIndex.KP7: "Bright at London",
            GeomagStormIndex.KP8: "Bright at northern France's latitude, visible from the Alps",
            GeomagStormIndex.KP9: "Bright at Paris, visible from southern Europe"
        }
    # end def
# end class


class HemisphereChoices(IntEnum):
    NORTH       = 1
    SOUTH       = 2
    BOTH        = 3
# end class


class Emojis(Enum):
    OK          = "\U0001F197"
    WAVE        = "\U0001F44B"
    WRENCH      = "\U0001F527"
    BELL        = "\U0001F514"
    GLOBE       = "\U0001F310"
    CLOCK       = "\U0001F551"
    MILKY_WAY   = "\U0001F30C"
    GRAPH       = "\U0001F4CA"
    QUESTION    = "\U00002753"
# end class
