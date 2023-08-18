from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

from yaml_extender.resolver.reference_resolver import ReferenceResolver
from yaml_extender.resolver.resolver import Resolver
from yaml_extender.xyml_exception import RecursiveReferenceError, ReferenceNotFoundError, ExtYamlSyntaxError

LOOP_KEY = "xyml.for"
INLINE_LOOP_REGEX = r'(\{\{\s*xyml\.for\s*:\s*([^:]+)\s*:\s*([^:]+)\s*:(.+)\}\})'
MAXIMUM_REFERENCE_DEPTH = 30


class InlineLoopResolver(Resolver):

    def __init__(self, fail_on_resolve: bool = True):
        super().__init__(fail_on_resolve)
        self.ref_resolver = ReferenceResolver(False)

    def _Resolver__resolve(self, cur_value: Any, config: dict):
        """Resolves all references in a given value using the provided content dict"""
        new_value = cur_value
        if isinstance(cur_value, dict):
            for k in cur_value.keys():
                cur_value[k] = self._Resolver__resolve(cur_value[k], config)
        elif isinstance(cur_value, list):
            new_list = []
            for i, x in enumerate(cur_value):
                resolved_value = self._Resolver__resolve(x, config)
                if isinstance(resolved_value, list):
                    # If the returned value is also a list, extend the current list with it
                    new_list.extend(resolved_value)
                else:
                    new_list.append(self._Resolver__resolve(x, config))
            new_value = new_list
        elif isinstance(cur_value, str):
            new_value = self.resolve_inline_loop(cur_value, config)
        return new_value

    def resolve_inline_loop(self, value: str, config: dict):
        new_value = value
        for match in re.findall(INLINE_LOOP_REGEX, value):
            full_match = match[0]
            iterator = match[1]
            iteration_value = match[2]
            content = match[3]
            iter_content = config[iteration_value]
            if not isinstance(iter_content, list):
                raise ExtYamlSyntaxError(f"{iteration_value} is not iterable and therefore cannot be used in a loop.")
            new_content = self.get_loop_content(content, iterator, iter_content)
            new_value = new_value.replace(full_match, new_content)
        return new_value

    def get_loop_content(self, content: str, iterator: str, iteration_value: list):
        new_content = ""
        for item in iteration_value:
            new_content += str(self.ref_resolver.resolve(content, {iterator: item}))
        return new_content
