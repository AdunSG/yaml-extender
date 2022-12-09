from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.yaml_extender.resolver.resolver import Resolver
from src.yaml_extender.xyml_exception import RecursiveReferenceError, ReferenceNotFoundError, ExtYamlSyntaxError

LOOP_KEY = "xyml.for"
REFERENCE_REGEX = r'\{\{(.+?)(?::(.+?))?\}\}'
ARRAY_REGEX = r'(.*)?\[(\d*)\]'
MAXIMUM_REFERENCE_DEPTH = 30


class LoopResolver(Resolver):

    def __init__(self, root_yaml: str | Path, fail_on_resolve: bool = True):
        super().__init__(root_yaml, fail_on_resolve)

    def _Resolver__resolve(self, cur_value: Any, config: dict):
        """Resolves all references in a given value using the provided content dict"""
        new_value = cur_value
        if isinstance(cur_value, dict):
            for k in cur_value.keys():
                if k == LOOP_KEY:

                cur_value[k] = self._Resolver__resolve(cur_value[k], config)
        elif isinstance(cur_value, list):
            for i, x in enumerate(cur_value):
                cur_value[i] = self._Resolver__resolve(x, config)
        return new_value

    def resolve_loop(self, cur_value, config):
        if

