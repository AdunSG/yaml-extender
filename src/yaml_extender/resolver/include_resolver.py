from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, List

from yaml_extender.resolver.reference_resolver import ReferenceResolver
from yaml_extender.resolver.resolver import Resolver
from yaml_extender.xyml_exception import ExtYamlSyntaxError
import yaml_extender.logger as logger
import yaml_extender.yaml_loader as yaml_loader

INCLUDE_REGEX = r'([^<]+)\s*(?:<<(.*)>>)?'
INCLUDE_KEY = "xyml.include"


class IncludeResolver(Resolver):

    def __init__(self, root_yaml, fail_on_resolve: bool = True):
        super().__init__(root_yaml, fail_on_resolve)
        self.root_dir: Path = self.root_yaml.parent

    def _Resolver__resolve(self, cur_value: Any, config: dict) -> dict:
        return self.__resolve_inc(cur_value, config, self.root_yaml)

    def __resolve_inc(self, cur_value: Any, config: dict, parent_file: Path) -> Any:
        """
        Resolves all include statements in value

            Returns:
                The content of the original file with all includes resolved.
        """
        if isinstance(cur_value, dict):
            additional_content = {}
            for k in cur_value.keys():
                if k == INCLUDE_KEY:
                    include_content = self.__resolve_include_statement(cur_value[k], parent_file, config)
                    # Filter all values that are already defined in current context
                    if isinstance(include_content, dict):
                        include_content = {k: v for k, v in include_content.items() if k not in cur_value}
                        additional_content.update(include_content)
                    else:
                        return include_content
                else:
                    cur_value[k] = self.__resolve_inc(cur_value[k], config, parent_file)
            # Update current content with the included
            if additional_content:
                del cur_value[INCLUDE_KEY]
                cur_value.update(additional_content)
        elif isinstance(cur_value, list):
            new_content = []
            for i, x in enumerate(cur_value):
                new_value = (self.__resolve_inc(x, config, parent_file))
                if isinstance(new_value, list):
                    new_content.extend(new_value)
                else:
                    new_content.append(new_value)
            if new_content:
                cur_value = new_content
        return cur_value

    def __resolve_include_statement(self, value: List | str, original_file: Path, config: dict) -> dict:
        """Resolves an include statement and return the content"""
        if not isinstance(value, list):
            statements = [value]
        else:
            statements = value
        # Resolve all references in statement
        ref_resolver = ReferenceResolver.from_resolver(self)
        inc_contents = None
        for statement in statements:
            statement = ref_resolver.resolve(statement, config)
            # Resolve include parameters
            match = re.match(INCLUDE_REGEX, statement)
            inc_file = match.group(1)
            # Resolve references in filenames
            logger.info(f"Resolving Include '{inc_file}'")
            inc_content = self.__read_included_yaml(inc_file, original_file)
            # Resolve parameters in included file
            if match.group(2):
                parameters = self.__parse_include_parameters(match.group(2))
                inc_content = ref_resolver.resolve(inc_content, parameters)
            # Add include content to current content
            inc_resolver = IncludeResolver(inc_file, self.fail_on_resolve)
            inc_content = inc_resolver.__resolve_inc(inc_content, config, original_file)
            inc_contents = self.update_inc_content(inc_contents, inc_content)
        return inc_contents

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

    def __read_included_yaml(self, file_path: str, original_file: Path = ""):
        # First try path to root .yml file
        # Second try relative to cwd
        # Third try relative to including file
        abs_path = self.root_dir / file_path
        if not abs_path.is_file():
            abs_path = Path(os.getcwd()) / file_path
            if not abs_path.is_file() and original_file:
                abs_path = original_file.parent / file_path
        return yaml_loader.load(str(abs_path))
