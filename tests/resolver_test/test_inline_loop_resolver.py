import yaml
from yaml_extender.resolver.inline_loop_resolver import InlineLoopResolver


def test_basic_inline_loop():
    content = yaml.safe_load("""
array_1:
- 123
- 456
ref_val_1: "This string is{{ xyml.for:i:array_1: NUM is: {{i}} !!!}} nothing more."
""")
    expected = yaml.safe_load("""
array_1:
- 123
- 456
ref_val_1: "This string is NUM is: 123 !!! NUM is: 456 !!! nothing more."
""")
    inl_loop_resolver = InlineLoopResolver()
    result = inl_loop_resolver.resolve(content)

    assert result == expected


