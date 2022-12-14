from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

from src.yaml_extender.resolver.reference_resolver import ReferenceResolver
from src.yaml_extender.resolver.resolver import Resolver
from src.yaml_extender.xyml_exception import RecursiveReferenceError, ReferenceNotFoundError, ExtYamlSyntaxError

LOOP_KEY = "xyml.for"
LOOP_CONTENT_KEY = "xyml.content"
LOOP_REGEX = r'(.+):(.+)'
MAXIMUM_REFERENCE_DEPTH = 30


class LoopResolver(Resolver):

    def __init__(self, root_yaml: str | Path, fail_on_resolve: bool = True):
        super().__init__(root_yaml, fail_on_resolve)
        self.ref_resolver = ReferenceResolver(self.root_yaml, False)

    def _Resolver__resolve(self, cur_value: Any, config: dict):
        """Resolves all references in a given value using the provided content dict"""
        new_value = cur_value
        if isinstance(cur_value, dict):
            for k, v in cur_value.items():
                new_value[k] = self._Resolver__resolve(v, config)
            if LOOP_KEY in cur_value:
                new_value = self.resolve_loop(cur_value[LOOP_KEY], new_value, config)
        elif isinstance(cur_value, list):
            for i, x in enumerate(cur_value):
                cur_value[i] = self._Resolver__resolve(x, config)
        return new_value

    def resolve_loop(self, loop_desc, loop_content, config):
        loop_values = []
        # Retrieve value and iterator
        match = re.search(LOOP_REGEX, loop_desc)
        if not match or len(match.groups()) < 2:
            raise ExtYamlSyntaxError(f"No valid loop statement: {loop_desc}")
        iterator = match[1]
        iteration_value = config[match[2]]
        if not isinstance(iteration_value, list):
            raise ExtYamlSyntaxError(f"No valid loop statement: {loop_desc}")

        # Remove loop statement from dict
        del loop_content[LOOP_KEY]
        if LOOP_CONTENT_KEY in loop_content:
            if len(loop_content) > 1:
                raise ExtYamlSyntaxError(f"Flat Loop content does not allow other mapping values: {loop_desc}")
            loop_content = loop_content[LOOP_CONTENT_KEY]
            for item in iteration_value:
                target_value = copy.deepcopy(loop_content)
                target_value = self.ref_resolver.resolve(target_value, {iterator: item})
                loop_values.extend(target_value)
        else:
            for item in iteration_value:
                target_value = copy.deepcopy(loop_content)
                target_value = self.ref_resolver.resolve(target_value, {iterator: item})
                loop_values.append(target_value)
        return loop_values

