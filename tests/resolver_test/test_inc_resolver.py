from pathlib import Path
from unittest import mock
import yaml

from src.yaml_extender.resolver.include_resolver import IncludeResolver


@mock.patch('yaml_extender.yaml_loader.load')
@mock.patch('pathlib.Path.is_file')
def test_basic_include(is_file_mock, load_func):
    is_file_mock.return_value = True
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
    inc_resolver = IncludeResolver()
    result = inc_resolver.resolve(content)

    assert load_func.call_args[0][0] == str(Path.cwd() / "inc.yaml")
    assert result == expected


@mock.patch('yaml_extender.yaml_loader.load')
@mock.patch('pathlib.Path.is_file')
def test_multiple_include(is_file_mock, load_func):
    is_file_mock.return_value = True
    content = yaml.safe_load("""
xyml.include: properties.yaml
dict_1:
  subvalue_1: abc
  xyml.include:
  - inc1.yaml
  - inc2.yaml
""")
    expected = yaml.safe_load("""
    glob_val: const
    dict_1:
      subvalue_1: abc
      subvalue_2: xyz
      subvalue_3:
        subvalue_4: 123
        subvalue_5: 456
    """)
    load_func.side_effect = [{"glob_val": "const"},
                             {"subvalue_2": "xyz"},
                             {"subvalue_3": {"subvalue_4": 123, "subvalue_5": 456}}]
    inc_resolver = IncludeResolver()
    result = inc_resolver.resolve(content)

    assert result == expected
    assert load_func.call_args_list[0][0][0] == str(Path.cwd() / "properties.yaml")
    assert load_func.call_args_list[1][0][0] == str(Path.cwd() / "inc1.yaml")
    assert load_func.call_args_list[2][0][0] == str(Path.cwd() / "inc2.yaml")


@mock.patch('yaml_extender.yaml_loader.load')
@mock.patch('pathlib.Path.is_file')
def test_recursive_include(is_file_mock, load_func):
    is_file_mock.return_value = True
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
    inc_resolver = IncludeResolver()
    result = inc_resolver.resolve(content)

    assert load_func.call_args_list[0][0][0] == str(Path.cwd() / "inc1.yaml")
    assert load_func.call_args_list[1][0][0] == str(Path.cwd() / "inc2.yaml")
    assert result == expected


@mock.patch('yaml_extender.yaml_loader.load')
@mock.patch('pathlib.Path.is_file')
def test_parameter_include(is_file_mock, load_func):
    is_file_mock.return_value = True
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
    inc_resolver = IncludeResolver()
    result = inc_resolver.resolve(content)

    assert load_func.call_args[0][0] == str(Path.cwd() / "inc.yaml")
    assert result == expected


@mock.patch('yaml_extender.yaml_loader.load')
@mock.patch('pathlib.Path.is_file')
def test_parameter_include_overwrite(is_file_mock, load_func):
    is_file_mock.return_value = True
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
    inc_resolver = IncludeResolver()
    result = inc_resolver.resolve(content)

    assert load_func.call_args[0][0] == str(Path.cwd() / "inc.yaml")
    assert result == expected


@mock.patch('yaml_extender.yaml_loader.load')
@mock.patch('pathlib.Path.is_file')
def test_parameter_include_partly_overwrite(is_file_mock, load_func):
    is_file_mock.return_value = True
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
    inc_resolver = IncludeResolver()
    result = inc_resolver.resolve(content)

    assert load_func.call_args[0][0] == str(Path.cwd() / "inc.yaml")
    assert result == expected


@mock.patch('yaml_extender.yaml_loader.load')
@mock.patch('pathlib.Path.is_file')
def test_additional_include_dir(is_file_mock, load_func):
    is_file_mock.return_value = True
    content = yaml.safe_load("""
dict_1:
  subvalue_1: abc
  xyml.include: inc.yaml
""")
    additional_inc_dir = Path("/usr/me")
    additional_fake_inc_dir = Path("/tmp/me")
    load_func.return_value = {"subvalue_2": "xyz", "subvalue_3": 123}
    inc_resolver = IncludeResolver([additional_inc_dir, additional_fake_inc_dir])
    _ = inc_resolver.resolve(content)
    assert load_func.call_args[0][0] == str(additional_inc_dir / "inc.yaml")


@mock.patch('yaml_extender.yaml_loader.load')
@mock.patch('pathlib.Path.is_file')
def test_array_include(is_file_mock, load_func):
    is_file_mock.return_value = True
    content = yaml.safe_load("""
array_1:
  xyml.include: inc.yaml
""")
    load_func.return_value = [{"subvalue_2": "xyz", "subvalue_3": 123}]
    expected = yaml.safe_load("""
    array_1:
    - subvalue_2: xyz
      subvalue_3: 123
    """)
    inc_resolver = IncludeResolver()
    result = inc_resolver.resolve(content)
    assert load_func.call_args[0][0] == str(Path.cwd() / "inc.yaml")
    assert result == expected


@mock.patch('yaml_extender.yaml_loader.load')
@mock.patch('pathlib.Path.is_file')
def test_multiple_array_include(is_file_mock, load_func):
    is_file_mock.return_value = True
    content = yaml.safe_load("""
array_1:
- xyml.include: inc1.yaml
- xyml.include: inc2.yaml
""")
    load_func.return_value = [{"subvalue_2": "xyz", "subvalue_3": 123}]
    expected = yaml.safe_load("""
    array_1:
    - subvalue_2: xyz
      subvalue_3: 123
    - subvalue_2: xyz
      subvalue_3: 123
    """)
    inc_resolver = IncludeResolver()
    result = inc_resolver.resolve(content)
    assert load_func.call_args_list[0][0][0] == str(Path.cwd() / "inc1.yaml")
    assert load_func.call_args_list[1][0][0] == str(Path.cwd() / "inc2.yaml")
    assert result == expected


@mock.patch('yaml_extender.yaml_loader.load')
@mock.patch('pathlib.Path.is_file')
def test_bool_value(is_file_mock, load_func):
    is_file_mock.return_value = True
    content = yaml.safe_load("""
value_1: abc
param_value: false
xyml.include: inc.yaml<<param_value=true>>
""")
    load_func.return_value = {"subvalue_2": "{{param_value}}", "subvalue_3": 123}
    expected = yaml.safe_load("""
    value_1: abc
    param_value: false
    subvalue_2: true
    subvalue_3: 123
    """)
    inc_resolver = IncludeResolver()
    result = inc_resolver.resolve(content)
    assert result == expected
