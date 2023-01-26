import os
from pathlib import Path

import yaml
from unittest.mock import patch

from src.yaml_extender.resolver.reference_resolver import ReferenceResolver
from src.yaml_extender.xyml_file import XYmlFile
from src.yaml_extender import yaml_loader


def test_basic_ref():
    content = yaml.safe_load("""
ref_val_1: 123
dict_1:
  subvalue_1: abc
  subvalue_2: "{{ref_val_1}}"
""")
    expected = yaml.safe_load("""
ref_val_1: 123
dict_1:
  subvalue_1: abc
  subvalue_2: 123
""")
    ref_resolver = ReferenceResolver("root.yaml")
    result = ref_resolver.resolve(content)

    assert result == expected


def test_recursive_ref():
    content = yaml.safe_load("""
ref_val_1: 123
ref_val_2: "{{ref_val_3}}_xyz"
ref_val_3: abc_{{ref_val_1}}
""")
    expected = yaml.safe_load("""
ref_val_1: 123
ref_val_2: abc_123_xyz
ref_val_3: abc_123
""")
    ref_resolver = ReferenceResolver("root.yaml")
    result = ref_resolver.resolve(content)

    assert result == expected


def test_dict_ref():
    content = yaml.safe_load("""
ref_val_1: "{{dict_1.subvalue_2}}"
dict_1:
  subvalue_1: abc
  subvalue_2: 123
""")
    expected = yaml.safe_load("""
ref_val_1: 123
dict_1:
  subvalue_1: abc
  subvalue_2: 123
""")
    ref_resolver = ReferenceResolver("root.yaml")
    result = ref_resolver.resolve(content)

    assert result == expected


def test_array_ref():
    content = yaml.safe_load("""
ref_val_1: "{{array_1[1]}}"
array_1:
- abc
- xyz
- 123
""")
    expected = yaml.safe_load("""
ref_val_1: xyz
array_1:
- abc
- xyz
- 123
""")
    ref_resolver = ReferenceResolver("root.yaml")
    result = ref_resolver.resolve(content)

    assert result == expected


def test_array_in_dict_ref():
    content = yaml.safe_load("""
ref_val_1: "{{dict_1.subvalue_2[1].config}}"
dict_1:
  subvalue_1: const_val
  subvalue_2:
  - path: first/path
    config: first.cfg
  - path: second/path
    config: second.cfg
""")
    expected = yaml.safe_load("""
ref_val_1: second.cfg
dict_1:
  subvalue_1: const_val
  subvalue_2:
  - path: first/path
    config: first.cfg
  - path: second/path
    config: second.cfg
""")
    ref_resolver = ReferenceResolver("root.yaml")
    result = ref_resolver.resolve(content)

    assert result == expected


def test_basic_default_value():
    content = yaml.safe_load("""
ref_val_1: 123
dict_1:
  subvalue_1: abc
  subvalue_2: "{{ref_val_2:default}}"
""")
    expected = yaml.safe_load("""
ref_val_1: 123
dict_1:
  subvalue_1: abc
  subvalue_2: default
""")
    ref_resolver = ReferenceResolver("root.yaml")
    result = ref_resolver.resolve(content)

    assert result == expected


def test_numeric_default_value():
    content = yaml.safe_load("""
ref_val_1: abc
ref_val_2: "{{ not_existing:123 }}"
""")
    expected = yaml.safe_load("""
ref_val_1: abc
ref_val_2: 123
""")
    ref_resolver = ReferenceResolver("root.yaml")
    result = ref_resolver.resolve(content)

    assert result == expected


def test_null_default_value():
    content = yaml.safe_load("""
ref_val_1: 123
dict_1:
  subvalue_1: abc
  subvalue_2: my_str_{{ref_val_2:}}
""")
    expected = yaml.safe_load("""
ref_val_1: 123
dict_1:
  subvalue_1: abc
  subvalue_2: my_str_
""")
    ref_resolver = ReferenceResolver("root.yaml")
    result = ref_resolver.resolve(content)

    assert result == expected


def test_array_default_value():
    content = yaml.safe_load("""
ref_val_1: "{{array_1[4]:default}}"
array_1:
- abc
- xyz
- 123
""")
    expected = yaml.safe_load("""
ref_val_1: default
array_1:
- abc
- xyz
- 123
""")
    ref_resolver = ReferenceResolver("root.yaml")
    result = ref_resolver.resolve(content)

    assert result == expected


def test_dict_default_value():
    content = yaml.safe_load("""
ref_val_1: "{{ dict_1.subvalue_3:default }}"
dict_1:
  subvalue_1: abc
  subvalue_2: 123
""")
    expected = yaml.safe_load("""
ref_val_1: default
dict_1:
  subvalue_1: abc
  subvalue_2: 123
""")
    ref_resolver = ReferenceResolver("root.yaml")
    result = ref_resolver.resolve(content)

    assert result == expected


def test_arithmetic_ref():
    content = yaml.safe_load("""
value_1: 1
value_2: "{{value_1+1}}"
""")
    expected = yaml.safe_load("""
value_1: 1
value_2: 2
""")
    ref_resolver = ReferenceResolver("root.yaml")
    result = ref_resolver.resolve(content)

    assert result == expected

    content = yaml.safe_load("""
    value_1: 1
    value_2: string_{{value_1+1}}
    """)
    expected = yaml.safe_load("""
    value_1: 1
    value_2: string_2
    """)
    ref_resolver = ReferenceResolver("root.yaml")
    result = ref_resolver.resolve(content)

    assert result == expected


@patch('src.yaml_extender.yaml_loader.load')
def test_env_ref(loader_mock):
    os.environ["TEST_VAL"] = "123"
    content = yaml.safe_load("""
value_1: 1
value_2: "{{ xyml.env.TEST_VAL}}"
""")
    loader_mock.return_value = content
    file = XYmlFile(Path.cwd())
    expected = yaml.safe_load("""
value_1: 1
value_2: "123"
""")
    assert file.content == expected

    # Test as default value
    content = yaml.safe_load("""
    value_1: 1
    value_2: "{{ undefined_value:{{ xyml.env.TEST_VAL}}}}"
    """)
    loader_mock.return_value = content
    file = XYmlFile(Path.cwd())
    assert file.content == expected


@patch('src.yaml_extender.yaml_loader.load')
def test_param_ref(loader_mock):
    content = yaml.safe_load("""
    value_1: 1
    value_2: "{{ xyml.param.test_param}}"
    """)
    loader_mock.return_value = content
    file = XYmlFile(Path.cwd(), {"test_param": 123})
    expected = yaml.safe_load("""
    value_1: 1
    value_2: 123
    """)

    assert file.content == expected

    # Test as default value
    content = yaml.safe_load("""
    value_1: 1
    value_2: "{{ undefined_value:{{ xyml.param.test_param}}}}"
    """)
    loader_mock.return_value = content
    file = XYmlFile(Path.cwd(), {"test_param": 123})
    assert file.content == expected



