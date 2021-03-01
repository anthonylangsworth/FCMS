# Work in progress!
# Mock EDMC-provided functionality to:
# 1. Stop `flake8` flagging errors.
# 2. Allow unit testing.

from typing import Any

try:
    _("a")
except NameError:
    def _(s):
        return s

try:
    config.get()
except NameError:
    class Config():
        def __init__(self):
            self._dict = dict()

        def get(self, key: str) -> Any:
            return self._dict.get(key, None)

        def set(self, key: str, value: Any) -> None:
            self._dict[key] = value

        def delete(self, key: str) -> None:
            del self._dict[key]
    config = Config()
