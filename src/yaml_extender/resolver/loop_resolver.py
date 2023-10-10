from __future__ import annotations

import copy
import re
from typing import Any

from yaml_extender.resolver.reference_resolver import ReferenceResolver
from yaml_extender.resolver.resolver import Resolver
from yaml_extender.xyml_exception import RecursiveReferenceError, ReferenceNotFoundError, ExtYamlSyntaxError

LOOP_KEY = "xyml.for"
LOOP_CONTENT_KEY = "xyml.content"
LOOP_REGEX = r'(.+):(.+)'
MAXIMUM_REFERENCE_DEPTH = 30


class LoopResolver(Resolver):

    def __init__(self, fail_on_resolve: bool = True):
        super().__init__(fail_on_resolve)
        self.ref_resolver = ReferenceResolver(False)

    def _Resolver__resolve(self, cur_value: Any, config: dict):
        """Resolves all references in a given value using the provided content dict"""
        new_value = cur_value
        if isinstance(cur_value, dict):
            for k, v in cur_value.items():
                new_value[k] = self._Resolver__resolve(v, config)
            if LOOP_KEY in cur_value:
                new_value = self.resolve_loop(cur_value[LOOP_KEY], copy.deepcopy(new_value), config)
        elif isinstance(cur_value, list):
            for i, x in enumerate(cur_value):
                resolved_loop_content = self._Resolver__resolve(x, config)
                if isinstance(resolved_loop_content, list):
                    # Keep list flat; don't create list of lists
                    del new_value[i]
                    for j, value in enumerate(resolved_loop_content):
                        # Make sure to insert the element at the position of loop statement
                        # Also take care of already inserted loop elements
                        new_value.insert(i + j, value)
                else:
                    new_value[i] = resolved_loop_content
        return new_value

    def resolve_loop(self, loop_desc, loop_config, config):
        other_content = []
        # Remove loop statement from dict
        del loop_config[LOOP_KEY]
        # Set initial value for resolution
        if LOOP_CONTENT_KEY in loop_config:
            loop_values = [loop_config[LOOP_CONTENT_KEY]]
            del loop_config[LOOP_CONTENT_KEY]
            # Keep track of values that might be in the same dict, but have nothing to do with the loop
            if loop_config:
                other_content = [loop_config]
        else:
            loop_values = [loop_config]
        # Iterate over possible multiloops
        loops = loop_desc.split(",")
        for loop in loops:
            # Retrieve value and iterator
            match = re.search(LOOP_REGEX, loop)
            if not match or len(match.groups()) < 2:
                raise ExtYamlSyntaxError(f"No valid loop statement: {loop}")
            iterator = match[1].strip()
            iteration_value = config[match[2].strip()]
            if not isinstance(iteration_value, list):
                raise ExtYamlSyntaxError(f"No valid loop statement: {loop}")

            # Replace the content with filled content
            loop_values = self.get_loop_content(loop_values, iteration_value, iterator)
        if other_content:
            loop_values = other_content + loop_values
        return loop_values

    def get_loop_content(self, loop_configs: list[dict], iteration_value: list, iterator: str):
        loop_values = []
        for loop_config in loop_configs:
            for item in iteration_value:
                target_value = copy.deepcopy(loop_config)
                target_value = self.ref_resolver.resolve(target_value, {iterator: item})
                if isinstance(target_value, list):
                    loop_values.extend(target_value)
                else:
                    loop_values.append(target_value)
        return loop_values
