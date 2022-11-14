import argparse
import logging
import sys

from pathlib import Path

from src.yaml_extender.xyml_file import XYmlFile

LOGGER = logging.getLogger()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input yaml file to be parsed", type=Path)
    parser.add_argument("output", help="Output file to save to", type=Path)
    args = parser.parse_args()

    if not args.input.is_file:
        raise FileNotFoundError(f"Path {args.input} is no valid file.")
    xyml_file = XYmlFile(args.input)
    output_dir: Path = args.output.parent
    output_dir.mkdir(exist_ok=True, parents=True)
    xyml_file.save(args.output)


if __name__ == "__main__":
    sys.exit(main())
