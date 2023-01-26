__version__ = '0.0.0.dev0'

import sys

from src.yaml_extender.xyml_file import XYmlFile
from src.yaml_extender.main import main

if __name__ == "__main__":
    sys.exit(main())
