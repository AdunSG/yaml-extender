class ExtYamlError(Exception):
    pass


class ReferenceNotFoundError(ExtYamlError):
    def __init__(self, reference: str, subref: str = ""):
        self.reference = reference
        self.subref = subref
        self.message = f"Unable to resolve {reference}"
        if self.subref:
            self.message += f" specified sub value {self.subref} not found."


class ExtYamlSyntaxError(ExtYamlError):
    pass


class RecursiveReferenceError(RecursionError):
    def __init__(self, reference):
        self.message = (
            f"Maximum recursive depth reached, while resolving {reference}. Is there a loop in your configuration?"
        )
