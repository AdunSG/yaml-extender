import yaml

from pathlib import Path
from src.yaml_extender.resolver.include_resolver import IncludeResolver, ReferenceResolver

context = None


class XYmlFile:

    def __init__(self, filepath: Path):
        self.filepath = filepath.absolute()
        self.root_dir = filepath.parent
        self.content = XYmlFile.load(str(self.filepath))
        self.content = self.resolve(self.filepath)

    def resolve(self, filepath):
        inc_resolver = IncludeResolver(self.filepath, False)
        processed_content = inc_resolver.resolve(self.content)


        processed_content = self.preprocess(processed_content, filepath)
        processed_content = self.postprocess(processed_content)
        return processed_content

    def save(self, path: str):
        with open(path, 'w') as file:
            yaml.dump(self.content, file)


