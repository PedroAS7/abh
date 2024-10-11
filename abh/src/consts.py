"""
Copyright 2024 PeterAS17 (www.peteras17.me)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from enum import IntEnum
from enum import Enum


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
    M5  = -45
    X1  = -40
    X5  = -35
    X10 = -30
    X20 = -31
    
    @staticmethod
    def get_help() -> dict[object, str]:
        # https://svs.gsfc.nasa.gov/10109/
        return {
            SolarFlareClass.M5:  "Moderate (350 per solar cycle). Might trigger a lot of alerts",
            SolarFlareClass.X1:  "Strong (175 per solar cycle)",
            SolarFlareClass.X5:  "Very strong (75 per solar cycle)",
            SolarFlareClass.X10: "Severe (8 per solar cycle)",
            SolarFlareClass.X20: "Extreme (1 per solar cycle)"
        }
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
