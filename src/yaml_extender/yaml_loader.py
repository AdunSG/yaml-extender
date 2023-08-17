from pathlib import Path
import yaml

VALID_YAML_SUFFIXES = [".yaml", ".yml", ".xyml"]


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


def parse_numeric_value(value: str):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"{value} is not a numeric value.")


def parse_any_value(value: str):
    try:
        return parse_numeric_value(value)
    except ValueError:
        try:
            return parse_bool_value(value)
        except ValueError:
            return value


def parse_bool_value(value: str):
    if value == "true":
        return True
    if value == "false":
        return False
    raise ValueError(f"{value} is not a boolean value.")
