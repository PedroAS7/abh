from os.path import exists
from json import load
from enum import Enum


class ConfigKeyType(Enum):
    BOT_TOKEN = 0
    DEBUG_MODE = BOT_TOKEN + 1
# end class


class _ConfigKey():

    def __init__(self,
                 key_type: ConfigKeyType,
                 key: str,
                 name: str,
                 default=None,
                 mandatory: bool = False) -> None:
        self._type = key_type
        self._key = key
        self._name = name
        self._value = default
        self._locked = False
        self._mandatory = mandatory
    # end def
    
    def is_set(self) -> bool:
        return self._value is not None
    # end def

    def set_value(self, value):
        if self._locked:
            raise RuntimeError("Configuration key has already been set")
        # end if

        self._value = value
        self._locked = True
    # end def

    def __repr__(self) -> str:
        return f"Config key '{self.name}'"
    # end def

    @property
    def type(self) -> ConfigKeyType:
        return self._type
    # end def

    @property
    def name(self) -> str:
        return self._name
    # end def

    @property
    def key(self) -> str:
        return self._key
    # end def

    @property
    def value(self) -> str:
        return self._value
    # end def

    @property
    def mandatory(self) -> str:
        return self._mandatory
    # end def
# end def


class Config():

    _CFG_FILENAME = "cfg.json"

    def __init__(self) -> None:
        self._cfg_list: list[_ConfigKey] = [
            _ConfigKey
            (
                ConfigKeyType.BOT_TOKEN,
                "token",
                "Bot token",
                mandatory=True
            ),
            _ConfigKey
            (
                ConfigKeyType.DEBUG_MODE,
                "debug",
                "Debug mode",
                default=False
            )
        ]
    # end def

    def __getitem__(self, key: ConfigKeyType) -> _ConfigKey:
        found_key: _ConfigKey = None
        for cfg_key in self._cfg_list:
            if key == cfg_key.type:
                found_key = cfg_key
                break
            # end if
        # end for

        if not found_key:
            raise ValueError("Invalid configuration key")
        # end if

        return found_key.value
    # end def

    @staticmethod
    def read():

        if not exists(Config._CFG_FILENAME):
            raise ValueError("Configuration file does not exist")
        # end if

        cfg_instance = Config()

        with open(Config._CFG_FILENAME, "rt") as cfg_file:
            cfg_json = load(cfg_file)

            if not cfg_json:
                raise ValueError("Invalid configuration file")
            # end if

            for field_key in cfg_json:
                field_value = cfg_json[field_key]
                
                found_key: _ConfigKey = None
                for cfg_key in cfg_instance._cfg_list:
                    if field_key == cfg_key.key:
                        found_key = cfg_key
                        break
                    # end if
                # end for

                if not found_key:
                    raise ValueError(f"Invalid configuration key {field_key}")
                # end if

                found_key.set_value(field_value)
            # end for
        # end with

        return cfg_instance
    # end def
# end class
