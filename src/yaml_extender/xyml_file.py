import os
import re
from typing import Any, Optional
import yaml

from pathlib import Path
import logger
from src.yaml_extender.XymlException import ReferenceNotFoundError, ExtYamlSyntaxError

ARRAY_REGEX = r'(.*)?\[(\d*)\]'
REFERENCE_REGEX = r'\{\{(.*?)\}\}'
INCLUDE_REGEX = r'(.*?)\s*(?:<<(.*)>>)'

VALID_YAML_SUFFIXES = [".yaml", ".yml"]


class XYmlFile:

    def __init__(self, filepath: Path):
        self.filepath = filepath.absolute()
        self.root_dir = filepath.parent
        self.fail_on_resolve = False
        self.content = XYmlFile.load(str(self.filepath))
        self.content = self.resolve(self.content, self.filepath)

    def resolve(self, content, filepath):
        processed_content = content
        processed_content = self.preprocess(processed_content, filepath)
        processed_content = self.postprocess(processed_content)
        return processed_content

    def preprocess(self, content, filepath):
        """Resolves all references of current file and all include statements"""
        processed_content = content
        self.fail_on_resolve = False
        processed_content = self.resolve_references("", processed_content, processed_content)
        processed_content = self.resolve_includes("", processed_content, str(filepath), processed_content)
        return processed_content

    def postprocess(self, content):
        """Resolves all references in this file including """
        processed_content = content
        self.fail_on_resolve = True
        processed_content = self.resolve_references("", processed_content, processed_content)
        return processed_content

    def resolve_includes(self, key: Any, value: Any, original_file: str, content: dict):
        """
        Resolves all include statements in value

            Parameters:
                key : str
                    The key for this value element
                value: Any
                    The value for which include statements should be resolved
                original_file:
                    The file containing the include statements
                content:
                    The values that should be used to resolve references

            Returns:
                THe content of the original file with all includes resolved.
        """
        new_dict = {}
        if isinstance(value, dict):
            for k, v in value.items():
                new_dict.update(self.resolve_includes(k, v, original_file, content))
        elif isinstance(value, list):
            for x in value:
                new_dict.update(self.resolve_includes("", x, original_file, content))
        else:
            if key == "include":
                include_content = self.resolve_include_statement(value, original_file, content)
                # Update this direction to throw away included values that are already defined
                new_dict = include_content.update(new_dict)
            else:
                new_dict[key] = value
        return new_dict

    def resolve_include_statement(self, statement: str, original_file: str, content: dict) -> dict:
        """Resolves a single include statement and return the content"""
        # Resolve include parameters
        match = re.match(INCLUDE_REGEX, statement)
        inc = match[1]
        logger.info(f"Resolving Include '{inc}'")
        inc_content = self.read_yaml(inc, original_file)
        # Resolve parameters in included file
        parameters = self.parse_include_parameters(match[2], content)
        inc_content = self.resolve_references("", inc_content, parameters)
        # Add include content to current content
        return self.preprocess(inc_content, inc)

    def parse_include_parameters(self, param_string: str, content: dict) -> dict:
        """Parses an include parameter string into a dict"""
        parameters = {}
        for param in param_string.split(","):
            key, value = param.split("=")
            if not key or not value:
                raise ExtYamlSyntaxError(f"Invalid parameter string {param_string}")
            parameters[key.strip()] = self.get_reference(value.strip(), content)
        return parameters

    def resolve_references(self, key: Any, value: Any, content: dict):
        """Resolves all references in a given value using the provided content dict"""
        new_dict = {}
        if isinstance(value, dict):
            for k, v in value.items():
                new_dict.update(self.resolve_references(k, v, content))
        elif isinstance(value, list):
            for x in value:
                new_dict.update(self.resolve_references("", x, content))
        else:
            new_value = self.get_reference(value, content)
            new_dict[key] = new_value
        return new_dict

    def get_reference(self, value: Any, content: dict):
        if not isinstance(value, str) or "{" not in value:
            return value
        new_value = value
        # In order to store the full match the whole regex is packed into a group
        full_match_regex = f"(?:{REFERENCE_REGEX})"
        matches = re.finditer(full_match_regex, value)
        for ref_match in matches:
            ref = ref_match.group(1)
            current_content = content
            for subref in ref.split('.'):
                # Resolve arrays
                arr_match = re.match(ARRAY_REGEX, subref)
                if arr_match:
                    if arr_match[0] in current_content:
                        if len(current_content[arr_match[0]]) > arr_match[1]:
                            current_content = current_content[arr_match[0]][arr_match[1]]
                        else:
                            raise ReferenceNotFoundError(arr_match[0] + f"[{arr_match[1]}]")
                    elif self.fail_on_resolve:
                        raise ReferenceNotFoundError(arr_match[0])
                else:
                    if subref in current_content:
                        current_content = current_content[subref]
                    elif self.fail_on_resolve:
                        raise ReferenceNotFoundError(subref)
            # Replace the reference string with the value
            if len(current_content) > 1:
                raise ExtYamlSyntaxError(f"Unable to resolve {value}. The referenced value contains more than 1 element.")
            ref_val = list(current_content.values())[0]
            new_value = new_value.replace(ref_match.group(0), ref_val)
        return new_value

    # def _resolve(self, key, value, resolve_fkt):
    #     if isinstance(value, dict):
    #         for k, v in value.items():
    #             self.resolve(k, v, resolve_fkt)
    #     elif isinstance(value, list):
    #         for x in value:
    #             self.resolve("", x, resolve_fkt)
    #     else:
    #         resolve_fkt(key, value)

    def read_yaml(self, file_path: str, original_file: str = ""):
        # First try path to root .yml file
        # Second try relative to cwd
        # Third try relative to including file
        abs_path = self.root_dir / file_path
        if not abs_path.is_file():
            abs_path = Path(os.getcwd()) / file_path
            if not abs_path.is_file() and original_file:
                abs_path = Path(original_file).parent / file_path
        return XYmlFile.load(str(abs_path))

    def save(self, path: str):
        with open(path, 'w') as file:
            yaml.dump(self.content, file)

    @staticmethod
    def load(path: str) -> dict:
        if not any(path.endswith(suffix) for suffix in VALID_YAML_SUFFIXES):
            # Add yaml suffix if the filepath is missing it
            possible_paths = [Path(path + suffix) for suffix in VALID_YAML_SUFFIXES]
            valid_paths = [p for p in possible_paths if p.is_file()]
            if valid_paths:
                valid_path = valid_paths[0]
            else:
                raise FileNotFoundError(f"Unable to resolve {path}")
        else:
            valid_path = Path(path)
            if not valid_path.is_file():
                raise FileNotFoundError(f"Unable to resolve {path}")
        with open(valid_path, 'r') as file:
            content = yaml.safe_load(file)
        return content
