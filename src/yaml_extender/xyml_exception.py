class ExtYamlError(Exception):
    pass


class ReferenceNotFoundError(ExtYamlError):

    def __init__(self, reference):
        self.message = f"Unable to resolve {reference}"


class ExtYamlSyntaxError(ExtYamlError):
    pass


class RecursiveReferenceError(RecursionError):

    def __init__(self, reference):
        self.message = f"Maximum recursive depth reached, while resolving {reference}." \
                       f"Is there a loop in your configuration?"
