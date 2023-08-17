import yaml

from src.yaml_extender.resolver.loop_resolver import LoopResolver


def test_loop_basic():
    content = yaml.safe_load("""
array_1:
- abc
- xyz
commands:
  xyml.for: iterator:array_1
  cmd: sh {{ iterator }}
  from: curDir
""")
    expected = yaml.safe_load("""
array_1:
- abc
- xyz
commands:
- cmd: sh abc
  from: curDir
- cmd: sh xyz
  from: curDir
""")
    loop_resolver = LoopResolver("root.yaml")
    result = loop_resolver.resolve(content)
    assert result == expected


def test_loop_subvalue():
    content = yaml.safe_load("""
array_1:
- value: abc
  path: first/path
- value: xyz
  path: second/path

commands:
  xyml.for: iterator:array_1
  cmd: sh {{ iterator.value }}
  from: "{{ iterator.path }}"
""")
    expected = yaml.safe_load("""
array_1:
- value: abc
  path: first/path
- value: xyz
  path: second/path

commands:
- cmd: sh abc
  from: first/path
- cmd: sh xyz
  from: second/path
""")
    loop_resolver = LoopResolver("root.yaml")
    result = loop_resolver.resolve(content)
    assert result == expected


def test_flat_loop():
    content = yaml.safe_load("""
array_1:
- abc
- xyz
commands:
  xyml.for: iterator:array_1
  xyml.content:
  - cmd: sh {{ iterator }}
  - cmd: echo {{ iterator }}
""")
    expected = yaml.safe_load("""
array_1:
- abc
- xyz
commands:
  - cmd: sh abc
  - cmd: echo abc
  - cmd: sh xyz
  - cmd: echo xyz
""")
    loop_resolver = LoopResolver("root.yaml")
    result = loop_resolver.resolve(content)
    assert result == expected


def test_stacked_loop():
    content = yaml.safe_load("""
array_1:
- abc
- xyz
array_2:
- 123
- 456
commands:
  xyml.for: i:array_1
  xyml.content:
    xyml.for: j:array_2
    cmd: sh {{ i }} {{ j }}
""")
    expected = yaml.safe_load("""
array_1:
- abc
- xyz
array_2:
- 123
- 456
commands:
- cmd: sh abc 123
- cmd: sh abc 456
- cmd: sh xyz 123
- cmd: sh xyz 456
""")
    loop_resolver = LoopResolver("root.yaml")
    result = loop_resolver.resolve(content)
    assert result == expected


def test_multiloop():
    content = yaml.safe_load("""
array_1:
- abc
- xyz
array_2:
- 123
- 456
commands:
  xyml.for: i:array_1, j:array_2
  xyml.content:
    cmd: sh {{i}} {{j}}
""")
    expected = yaml.safe_load("""
array_1:
- abc
- xyz
array_2:
- 123
- 456
commands:
- cmd: sh abc 123
- cmd: sh abc 456
- cmd: sh xyz 123
- cmd: sh xyz 456
""")
    loop_resolver = LoopResolver("root.yaml")
    result = loop_resolver.resolve(content)
    assert result == expected

