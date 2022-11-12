class ReferenceNotFoundError(Exception):

    def __init__(self, reference):
        self.message = f"Unable to resolve {reference}"


class ExtYamlSyntaxError(Exception):
    pass
