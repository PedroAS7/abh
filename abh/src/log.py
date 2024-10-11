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

from sys import platform
from colorama import just_fix_windows_console
from colorama import Fore
from colorama import Back
from colorama import Style

# Fix Windows terminal colors
if platform.startswith("win"):
    just_fix_windows_console()
# end if

# --
# Globals
# --

_indent_level = 0
_indent_max = 5


# --
# Functions
# --

def log(*what: object,
        fore: Fore = Fore.RESET,
        back: Back = Back.RESET,
        style: Style = Style.NORMAL,
        sep: str | None = " ",
        end: str | None = "\n") -> None:
    indent_str = '\t' * _indent_level if _indent_level > 0 else ''
    print(fore, back, style, indent_str, *what, Style.RESET_ALL, sep=sep, end=end)
# end def

def error(*what: object,
          sep: str | None = " ",
          end: str | None = "\n"):
    log(*what, fore=Fore.RED, back=Back.RESET, style=Style.BRIGHT, sep=sep, end=end)
# end def

def warn(*what: object,
         sep: str | None = " ",
         end: str | None = "\n"):
    log(*what, fore=Fore.BLACK, back=Back.YELLOW, style=Style.BRIGHT, sep=sep, end=end)
# end def

def debug(*what: object,
          sep: str | None = " ",
          end: str | None = "\n"):
    log(*what, fore=Fore.BLACK, back=Back.LIGHTCYAN_EX, style=Style.NORMAL, sep=sep, end=end)
# end def

def indent() -> None:
    global _indent_level
    _indent_level += 1 if _indent_level < _indent_max else _indent_max
# end def

def project() -> None:
    global _indent_level
    _indent_level -= 1 if _indent_level > 0 else 0
# end def
