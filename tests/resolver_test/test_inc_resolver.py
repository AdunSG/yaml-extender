from unittest import mock
import yaml

from src.yaml_extender.resolver.include_resolver import IncludeResolver


@mock.patch('yaml_extender.yaml_loader.load')
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


@mock.patch('yaml_extender.yaml_loader.load')
def test_multiple_include(load_func):
    content = yaml.safe_load("""
dict_1:
  subvalue_1: abc
  xyml.include:
  - inc1.yaml
  - inc2.yaml
""")
    expected = yaml.safe_load("""
    dict_1:
      subvalue_1: abc
      subvalue_2: xyz
      subvalue_3:
        subvalue_4: 123
        subvalue_5: 456
    """)
    load_func.side_effect = [{"subvalue_2": "xyz"},
                             {"subvalue_3": {"subvalue_4": 123, "subvalue_5": 456}}]
    inc_resolver = IncludeResolver("root.yaml")
    result = inc_resolver.resolve(content)

    assert load_func.call_args_list[0][0][0] == "inc1.yaml"
    assert load_func.call_args_list[1][0][0] == "inc2.yaml"
    assert result == expected


@mock.patch('yaml_extender.yaml_loader.load')
def test_recursive_include(load_func):
    content = yaml.safe_load("""
dict_1:
  subvalue_1: abc
  xyml.include: inc1.yaml
""")
    expected = yaml.safe_load("""
    dict_1:
      subvalue_1: abc
      subvalue_2: xyz
      subvalue_3: 123
    """)
    load_func.side_effect = [{"subvalue_2": "xyz", "xyml.include": "inc2.yaml"},
                             {"subvalue_3": 123}]
    inc_resolver = IncludeResolver("root.yaml")
    result = inc_resolver.resolve(content)

    assert load_func.call_args_list[0][0][0] == "inc1.yaml"
    assert load_func.call_args_list[1][0][0] == "inc2.yaml"
    assert result == expected


@mock.patch('yaml_extender.yaml_loader.load')
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


@mock.patch('yaml_extender.yaml_loader.load')
def test_parameter_include_overwrite(load_func):
    content = yaml.safe_load("""
    value_1: 123
    value_2: abc
    xyml.include: inc.yaml
    """)
    expected = yaml.safe_load("""
    value_1: 123
    value_2: abc
    value_3: 123
    """)
    load_func.return_value = {"value_2": "xyz", "value_3": 123}
    inc_resolver = IncludeResolver("root.yaml")
    result = inc_resolver.resolve(content)

    assert load_func.call_args[0][0] == "inc.yaml"
    assert result == expected


@mock.patch('yaml_extender.yaml_loader.load')
def test_parameter_include_partly_overwrite(load_func):
    content = yaml.safe_load("""
    dict_1:
      subvalue_1: abc
      subvalue_2: xyz
    xyml.include: inc.yaml
    """)
    expected = yaml.safe_load("""
    dict_1:
      subvalue_1: abc
      subvalue_2: xyz
      subvalue_3: 123
    """)
    load_func.return_value = {"dict_1": {"subvalue_2": "abc", "subvalue_3": 123}}
    inc_resolver = IncludeResolver("root.yaml")
    result = inc_resolver.resolve(content)

    assert load_func.call_args[0][0] == "inc.yaml"
    assert result == expected

