from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from yaml_extender import yaml_loader
from yaml_extender.resolver.resolver import Resolver
from yaml_extender.xyml_exception import RecursiveReferenceError, ReferenceNotFoundError, ExtYamlSyntaxError

REFERENCE_REGEX = r'\{\{(.+?)(?::(.*?))?\}\}'
ARRAY_REGEX = r'(.*)?\[(\d*)\]'
LIST_FLATTEN_CHARACTER = " "

MAXIMUM_REFERENCE_DEPTH = 30


class ArithmeticOperation:

    SUPPORTED_FUNCS = {"+": lambda x, y: x + y,
                       "-": lambda x, y: x - y,
                       "*": lambda x, y: x * y,
                       "/": lambda x, y: x / y}
    ARITHMETIC_REGEX = r'(.+)([' + ''.join(["\\" + k for k in SUPPORTED_FUNCS.keys()]) + r'])\s*(\d+)'

    def __init__(self, reference: str, operation: str, value: str):
        self.reference = reference.strip()
        self.operation = operation.strip()
        self.value = yaml_loader.parse_numeric_value(value.strip())

    def __repr__(self):
        return f"{self.reference} {self.operation} {self.value}"

    def apply(self, value):
        num_val = yaml_loader.parse_numeric_value(value)
        return ArithmeticOperation.SUPPORTED_FUNCS[self.operation](self.value, num_val)

    @staticmethod
    def parse(expression: str) -> Optional[ArithmeticOperation]:
        match = re.search(ArithmeticOperation.ARITHMETIC_REGEX, expression)
        if match:
            return ArithmeticOperation(match[1], match[2], match[3])
        else:
            return None


class ReferenceResolver(Resolver):

    def __init__(self, fail_on_resolve: bool = True):
        super().__init__(fail_on_resolve)

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
        else:
            new_value = self.resolve_reference(cur_value, config)
        return new_value

    def resolve_reference(self, value: Any, config: dict, depth: int = 0) -> Any:
        if not isinstance(value, str) or "{" not in value:
            return value
        if depth > 30:
            raise RecursiveReferenceError(value)
        new_value = value
        # In order to store the full match the whole regex is packed into a group
        for ref_match in re.finditer(REFERENCE_REGEX, value):
            ref = ref_match.group(1).strip()
            default_value = ref_match.group(2)
            if default_value:
                default_value = yaml_loader.parse_any_value(default_value.strip())
            failed = ""
            current_config = config
            # Resolve arithmetic operation
            operation = ArithmeticOperation.parse(ref)
            if operation:
                ref = operation.reference
            # Resolve reference, including subrefs
            split_ref = ref.split('.')
            for i, subref in enumerate(split_ref):
                # If subref is specifying more than config can resolve, e.g. for include parameter dicts
                # And the resolved value is another reference, append the subref and resolve later
                if isinstance(current_config, str):
                    match = re.match(REFERENCE_REGEX, current_config)
                    if match:
                        current_config = match.group(1).strip()
                        if match.group(2):
                            current_config += f":{match.group(2)}"
                        remaining_subrefs = ".".join(split_ref[i:])
                        current_config = "{{" + current_config + f".{remaining_subrefs}" + "}}"
                    else:
                        failed = subref
                    break
                # Resolve arrays
                arr_match = re.match(ARRAY_REGEX, subref)
                if arr_match:
                    array_name = arr_match[1]
                    try:
                        index = int(arr_match[2])
                    except TypeError:
                        raise TypeError(f"Unable to convert index of '{subref}' to integer.")
                    if array_name in current_config:
                        if len(current_config[array_name]) > index:
                            current_config = current_config[array_name][index]
                        else:
                            failed = array_name + f"[{index}]"
                            break
                    else:
                        failed = array_name
                        break
                else:
                    if subref in current_config:
                        current_config = current_config[subref]
                    else:
                        failed = subref
                        break
            if failed:
                if default_value is not None:
                    ref_val = default_value
                elif self.fail_on_resolve:
                    raise ReferenceNotFoundError(ref)
                else:
                    ref_val = None
            else:
                ref_val = current_config

            if ref_val is not None:
                if operation:
                    ref_val = operation.apply(ref_val)
                if ref_match.group(0) == value:
                    # If the whole string is just a reference return the value without string replacement
                    # in order to preserve float & int types
                    return ref_val
                else:
                    # Replace the reference string with the value
                    if isinstance(ref_val, list):
                        ref_val = LIST_FLATTEN_CHARACTER.join(ref_val)
                    new_value = new_value.replace(ref_match.group(0), str(ref_val))

        if new_value == value:
            if self.fail_on_resolve:
                raise ReferenceNotFoundError(value)
            else:
                return value

        # Resolve recursive references
        new_value = self.resolve_reference(new_value, config, depth + 1)
        return new_value

