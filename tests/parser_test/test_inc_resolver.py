import pathlib
import difflib
from typing import Iterator
from unittest import mock

import yaml
import pytest

from src.yaml_extender.resolver.include_resolver import IncludeResolver
from src.yaml_extender.xyml_exception import RecursiveReferenceError, ReferenceNotFoundError


res_path = pathlib.Path(__file__).parent.parent / "res"
out_suffix = ".tmp"     # Will get ignored by git


# @mock.patch('src.yaml_extender.yaml_loader.load')
# def test_basic_include(load_func):
#     content = yaml.safe_load("""
# dict_1:
#   subvalue_1: abc
#   xyml.include: inc.yaml
# """)
#     expected = yaml.safe_load("""
#     dict_1:
#       subvalue_1: abc
#       subvalue_2: xyz
#       subvalue_3: 123
#     """)
#     load_func.return_value = {"subvalue_2": "xyz", "subvalue_3": 123}
#     inc_resolver = IncludeResolver("root.yaml")
#     result = inc_resolver.resolve(content)
#
#     assert load_func.call_args[0][0] == "inc.yaml"
#     assert result == expected
#
#
# @mock.patch('src.yaml_extender.yaml_loader.load')
# def test_multiple_include(load_func):
#     content = yaml.safe_load("""
# dict_1:
#   subvalue_1: abc
#   xyml.include:
#   - inc1.yaml
#   - inc2.yaml
# """)
#     expected = yaml.safe_load("""
#     dict_1:
#       subvalue_1: abc
#       subvalue_2: xyz
#       subvalue_3:
#         subvalue_4: 123
#         subvalue_5: 456
#     """)
#     load_func.side_effect = [{"subvalue_2": "xyz"},
#                              {"subvalue_3": {"subvalue_4": 123, "subvalue_5": 456}}]
#     inc_resolver = IncludeResolver("root.yaml")
#     result = inc_resolver.resolve(content)
#
#     assert load_func.call_args_list[0][0][0] == "inc1.yaml"
#     assert load_func.call_args_list[1][0][0] == "inc2.yaml"
#     assert result == expected
#
#
# @mock.patch('src.yaml_extender.yaml_loader.load')
# def test_recursive_include(load_func):
#     content = yaml.safe_load("""
# dict_1:
#   subvalue_1: abc
#   xyml.include: inc1.yaml
# """)
#     expected = yaml.safe_load("""
#     dict_1:
#       subvalue_1: abc
#       subvalue_2: xyz
#       subvalue_3: 123
#     """)
#     load_func.side_effect = [{"subvalue_2": "xyz", "xyml.include": "inc2.yaml"},
#                              {"subvalue_3": 123}]
#     inc_resolver = IncludeResolver("root.yaml")
#     result = inc_resolver.resolve(content)
#
#     assert load_func.call_args_list[0][0][0] == "inc1.yaml"
#     assert load_func.call_args_list[1][0][0] == "inc2.yaml"
#     assert result == expected


@mock.patch('src.yaml_extender.yaml_loader.load')
def test_parameter_include(load_func):
    content = yaml.safe_load("""
dict_1:
  subvalue_1: abc
  xyml.include: inc.yaml<<subvalue_2=xyz>>
""")
    expected = yaml.safe_load("""
    dict_1:
      subvalue_1: abc
      subvalue_2: xyz
      subvalue_3: 123
    """)
    load_func.return_value = {"subvalue_2": "{{subvalue_2}}", "subvalue_3": 123}
    inc_resolver = IncludeResolver("root.yaml")
    result = inc_resolver.resolve(content)

    assert load_func.call_args[0][0] == "inc.yaml"
    assert result == expected
