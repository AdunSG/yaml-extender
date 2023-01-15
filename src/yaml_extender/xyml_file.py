import yaml

from pathlib import Path

from src.yaml_extender import yaml_loader
from src.yaml_extender.resolver.include_resolver import IncludeResolver
from src.yaml_extender.resolver.loop_resolver import LoopResolver
from src.yaml_extender.resolver.reference_resolver import ReferenceResolver

context = None


class XYmlFile:

    def __init__(self, filepath: Path):
        self.filepath = filepath.absolute()
        self.root_dir = filepath.parent
        self.content = yaml_loader.load(str(self.filepath))
        self.content = self.resolve()

    def __repr__(self):
        return yaml.dump(self.content)

    def resolve(self):
        inc_resolver = IncludeResolver(self.filepath, False)
        processed_content = inc_resolver.resolve(self.content)
        loop_resolver = LoopResolver(self.filepath, False)
        processed_content = loop_resolver.resolve(processed_content)
        ref_resolver = ReferenceResolver(self.filepath, False)
        processed_content = ref_resolver.resolve(processed_content)
        return processed_content

    def save(self, path: str):
        with open(path, 'w') as file:
            yaml.dump(self.content, file)


