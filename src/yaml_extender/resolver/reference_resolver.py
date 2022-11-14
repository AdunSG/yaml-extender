from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.yaml_extender.resolver.resolver import Resolver
from src.yaml_extender.xyml_exception import RecursiveReferenceError, ReferenceNotFoundError, ExtYamlSyntaxError

REFERENCE_REGEX = r'\{\{(.*?)\}\}'
ARRAY_REGEX = r'(.*)?\[(\d*)\]'
MAXIMUM_REFERENCE_DEPTH = 30


class ReferenceResolver(Resolver):

    def __init__(self, root_yaml: str | Path, fail_on_resolve: bool = True):
        super().__init__(root_yaml, fail_on_resolve)

    def _Resolver__resolve(self, cur_value: Any, config: dict):
        """Resolves all references in a given value using the provided content dict"""
        new_value = cur_value
        if isinstance(cur_value, dict):
            for k in cur_value.keys():
                cur_value[k] = self._Resolver__resolve(cur_value[k], config)
        elif isinstance(cur_value, list):
            for i, x in enumerate(cur_value):
                cur_value[i] = self._Resolver__resolve(x, config)
        else:
            new_value = self.get_reference(cur_value, config)
        return new_value

    def get_reference(self, value: Any, config: dict, depth: int = 0):
        if not isinstance(value, str) or "{" not in value:
            return value
        if depth > 30:
            raise RecursiveReferenceError(value)
        new_value = value
        # In order to store the full match the whole regex is packed into a group
        full_match_regex = f"(?:{REFERENCE_REGEX})"
        matches = re.finditer(full_match_regex, value)
        for ref_match in matches:
            ref = ref_match.group(1)
            current_config = config
            for subref in ref.split('.'):
                # Resolve arrays
                arr_match = re.match(ARRAY_REGEX, subref)
                if arr_match:
                    if arr_match[0] in current_config:
                        if len(current_config[arr_match[0]]) > arr_match[1]:
                            current_config = current_config[arr_match[0]][arr_match[1]]
                        else:
                            raise ReferenceNotFoundError(arr_match[0] + f"[{arr_match[1]}]")
                    elif self.fail_on_resolve:
                        raise ReferenceNotFoundError(arr_match[0])
                else:
                    if subref in current_config:
                        current_config = current_config[subref]
                    elif self.fail_on_resolve:
                        raise ReferenceNotFoundError(subref)
            # Replace the reference string with the value
            if len(current_config) > 1:
                raise ExtYamlSyntaxError(f"Unable to resolve {value}. The referenced value contains more than 1 element.")
            ref_val = list(current_config.values())[0]
            new_value = new_value.replace(ref_match.group(0), ref_val)
            # Resolve recursive references
            new_value = self.get_reference(new_value, config, depth + 1)
        return new_value
