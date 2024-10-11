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

import telegram


class TelegramUpdateParser():

    def can_handle(self, update: telegram.Update) -> bool:
        return False
    # end def

    async def parse(self, update: telegram.Update, app: object):
        raise NotImplementedError("Parser did not implement parser")
    # end def
# end class
