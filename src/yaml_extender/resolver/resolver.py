from __future__ import annotations

import abc
from pathlib import Path
from typing import Any


class Resolver(abc.ABC):

    def __init__(self, root_yaml: str | Path, fail_on_resolve: bool = True):
        """
        Parameters
            root_yaml: The root yaml where the resolution started
            fail_on_resolve: Flag if the parsing should be aborted if a value fails to resolve
        """
        self.root_yaml = Path(root_yaml)
        self.fail_on_resolve: bool = fail_on_resolve
        super().__init__()

    @classmethod
    def from_resolver(cls, other: "Resolver"):
        """Makes it easier to use Resolver from other Resolvers"""
        return cls(other.root_yaml, other.fail_on_resolve)

    def resolve(self, content: Any, config: dict = None) -> dict:
        if not config:
            config = content
        return self.__resolve(content, config)

    @abc.abstractmethod
    def __resolve(self, cur_value: Any, config: dict) -> dict:
        raise NotImplementedError
