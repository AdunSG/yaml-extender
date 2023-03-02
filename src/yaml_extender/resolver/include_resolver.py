from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, List

from yaml_extender.resolver.reference_resolver import ReferenceResolver
from yaml_extender.resolver.resolver import Resolver
from yaml_extender.xyml_exception import ExtYamlError, ExtYamlSyntaxError
import yaml_extender.logger as logger
import yaml_extender.yaml_loader as yaml_loader


INCLUDE_REGEX = r'([^<]+)\s*(?:<<(.*)>>)?'
INCLUDE_KEY = "xyml.include"


class IncludeResolver(Resolver):

    def __init__(self, include_dirs: List[Path] | None = None, fail_on_resolve: bool = True):
        if include_dirs:
            self.include_dirs: List[Path] = include_dirs
        else:
            self.include_dirs: List[Path] = []
        if Path.cwd() not in self.include_dirs:
            self.include_dirs.append(Path.cwd())
        super().__init__(fail_on_resolve)

    def _Resolver__resolve(self, cur_value: Any, config: dict) -> dict:
        return self.__resolve_inc(cur_value, config)

    def __resolve_inc(self, cur_value: Any, config: dict) -> Any:
        """
        Resolves all include statements in value

            Returns:
                The content of the original file with all includes resolved.
        """
        if isinstance(cur_value, dict):
            if INCLUDE_KEY in cur_value:
                include_content = self.__resolve_include_statement(cur_value[INCLUDE_KEY], config)
                if isinstance(include_content, dict):
                    self.update_content_with_include_content(cur_value, include_content)
                    del cur_value[INCLUDE_KEY]
                else:
                    if len(cur_value) > 1:
                        raise ExtYamlSyntaxError(f"Unable to resolve {cur_value}."
                                                 f"Included file does not return a dictionary.")
                    cur_value = include_content
            else:
                for k, v in cur_value.items():
                    cur_value[k] = self.__resolve_inc(cur_value[k], config)
        elif isinstance(cur_value, list):
            new_content = []
            for i, x in enumerate(cur_value):
                new_value = (self.__resolve_inc(x, config))
                if isinstance(new_value, list):
                    new_content.extend(new_value)
                else:
                    new_content.append(new_value)
            if new_content:
                cur_value = new_content
        return cur_value

    def __resolve_include_statement(self, value: List | str, config: dict) -> dict:
        """Resolves an include statement and return the content"""
        if not isinstance(value, list):
            statements = [value]
        else:
            statements = value
        # Resolve all references in statement
        ref_resolver = ReferenceResolver(False)
        inc_contents = None
        for statement in statements:
            statement = ref_resolver.resolve(statement, config)
            # Resolve include parameters
            match = re.match(INCLUDE_REGEX, statement)
            inc_file = match.group(1)
            # Resolve references in filenames
            logger.info(f"Resolving Include '{inc_file}'")
            inc_content = self.__read_included_yaml(inc_file)
            # Resolve parameters in included file
            if match.group(2):
                parameters = self.__parse_include_parameters(match.group(2))
                inc_content = ref_resolver.resolve(inc_content, parameters)
            # Add include content to current content
            include_dirs = self.include_dirs.copy()
            include_dirs.append(Path(inc_file).parent)
            inc_resolver = IncludeResolver(include_dirs, self.fail_on_resolve)
            inc_content = inc_resolver.__resolve_inc(inc_content, config)
            inc_contents = self.update_inc_content(inc_contents, inc_content)
        return inc_contents

    def update_content_with_include_content(self, existing_content, include_content):
        for k, v in include_content.items():
            if k in existing_content:
                if isinstance(v, dict):
                    self.update_content_with_include_content(existing_content[k], v)
            else:
                existing_content[k] = v

    def update_inc_content(self, content, include):
        """Adds include content to existing content based on current datatype"""
        if content is None:
            return include
        if isinstance(include, list):
            if isinstance(content, dict):
                content = [content]
            content.extend(include)
        elif isinstance(include, dict):
            if isinstance(content, list):
                content.append(include)
            else:
                content.update(include)
        else:
            raise ExtYamlSyntaxError("Resolved include content is not of list or dict type.")
        return content

    def __parse_include_parameters(self, param_string: str) -> dict:
        """Parses an include parameter string into a dict"""
        parameters = {}
        for param in param_string.split(","):
            key, value = param.split("=")
            if not key or not value:
                raise ExtYamlSyntaxError(f"Invalid parameter string {param_string}")
            parameters[key.strip()] = yaml_loader.parse_numeric_value(value.strip())
        return parameters

    def __read_included_yaml(self, file_path: str):
        # Try path with all include dirs respecting the order
        file = Path(file_path)
        if not file.is_absolute():
            for path in self.include_dirs:
                file = path / file_path
                if file.is_file():
                    return yaml_loader.load(str(file))
        raise ExtYamlError(f"Include file '{file_path}' not found. Are include directories provided?")
