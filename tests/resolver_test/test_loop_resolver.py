import pathlib
import difflib
from typing import Iterator
from unittest import mock

import yaml
import pytest

from src.yaml_extender.resolver.include_resolver import IncludeResolver
from src.yaml_extender.xyml_exception import RecursiveReferenceError, ReferenceNotFoundError


@mock.patch('src.yaml_extender.yaml_loader.load')
def test_basic_include(load_func):
    content = yaml.safe_load("""
dict_1:
  subvalue_1: abc
  xyml.include: inc.yaml
""")
    expected = yaml.safe_load("""
    dict_1:
      subvalue_1: abc
      subvalue_2: xyz
      subvalue_3: 123
    """)
    load_func.return_value = {"subvalue_2": "xyz", "subvalue_3": 123}
    inc_resolver = IncludeResolver("root.yaml")
    result = inc_resolver.resolve(content)

    assert load_func.call_args[0][0] == "inc.yaml"
    assert result == expected
