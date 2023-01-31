import argparse
import logging
import sys

from pathlib import Path
from typing import List, Dict

from src.yaml_extender.resolver import reference_resolver
from src.yaml_extender.xyml_file import XYmlFile

LOGGER = logging.getLogger()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input yaml file to be parsed", type=Path)
    parser.add_argument("output", help="Output file to save to", type=Path)
    args, additional_args = parser.parse_known_args()

    if not args.input.is_file:
        raise FileNotFoundError(f"Path {args.input} is no valid file.")
    xyml_file = XYmlFile(args.input, parse_unknown_args(additional_args))
    output_dir: Path = args.output.parent
    output_dir.mkdir(exist_ok=True, parents=True)
    xyml_file.save(args.output)


def parse_unknown_args(args: List) -> Dict:
    arg_dict = dict(zip(args[:-1:2], args[1::2]))
    ret_val = {}
    # Parse numbers from strings
    for k, v in arg_dict.items():
        ret_val[k.strip("-")] = reference_resolver.number_parse(v)
    return ret_val


if __name__ == "__main__":
    sys.exit(main())
