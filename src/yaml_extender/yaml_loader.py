from pathlib import Path
import yaml

VALID_YAML_SUFFIXES = [".yaml", ".yml"]


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
            return value
