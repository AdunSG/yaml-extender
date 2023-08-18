from __future__ import annotations

import os
import yaml
from typing import Dict, List
from pathlib import Path

from yaml_extender import yaml_loader
from yaml_extender.resolver.include_resolver import IncludeResolver
from yaml_extender.resolver.inline_loop_resolver import InlineLoopResolver
from yaml_extender.resolver.loop_resolver import LoopResolver
from yaml_extender.resolver.reference_resolver import ReferenceResolver

ENV_KEY = "env"
PARAM_KEY = "param"


class XYmlFile:

    def __init__(self, filepath: Path, params: Dict = None, include_dirs: List[Path] | None = None):
        self.params = params
        if include_dirs:
            self.include_dirs: List[Path] = include_dirs
        else:
            self.include_dirs: List[Path] = []
        self.filepath = filepath.absolute()
        self.root_dir = filepath.parent
        # Use root_dir and cwd as default include paths.
        if self.root_dir not in self.include_dirs:
            self.include_dirs.append(self.root_dir)
        if Path.cwd() not in self.include_dirs:
            self.include_dirs.append(Path.cwd())
        self.content = yaml_loader.load(str(self.filepath))
        self.content = self.resolve()

    def __repr__(self):
        return yaml.dump(self.content)

    def resolve(self):
        inc_resolver = IncludeResolver(self.include_dirs, False)
        processed_content = inc_resolver.resolve(self.content)
        loop_resolver = LoopResolver(False)
        processed_content = loop_resolver.resolve(processed_content)
        inline_loop_resolver = InlineLoopResolver(False)
        processed_content = inline_loop_resolver.resolve(processed_content)
        # Extend config for resolution by ENV and PARAM statements
        config = processed_content.copy()
        config["xyml"] = {}
        config["xyml"][ENV_KEY] = os.environ
        config["xyml"][PARAM_KEY] = self.params
        ref_resolver = ReferenceResolver(False)
        processed_content = ref_resolver.resolve(processed_content, config)
        return processed_content

    def save(self, path: str, sort_keys=False):
        with open(path, 'w') as file:
            yaml.dump(self.content, file, sort_keys=sort_keys)


