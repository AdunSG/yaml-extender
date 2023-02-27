from __future__ import annotations

import abc
from pathlib import Path
from typing import Any


class Resolver(abc.ABC):

    def __init__(self, fail_on_resolve: bool = True):
        """
        Parameters
            fail_on_resolve: Flag if the parsing should be aborted if a value fails to resolve
        """
        self.fail_on_resolve: bool = fail_on_resolve
        super().__init__()

    def resolve(self, content: Any, config: dict = None) -> dict:
        if not config:
            config = content
        return self.__resolve(content, config)

    @abc.abstractmethod
    def __resolve(self, cur_value: Any, config: dict) -> dict:
        raise NotImplementedError
