"""
Component Tests to test overall functionality of yaml_extender
"""
import yaml
from pathlib import Path

from src.yaml_extender.xyml_file import XYmlFile

script_dir = Path(__file__).parent
res_dir = script_dir.parent / "resources"


def test_reference_file():
    resolved_file = XYmlFile(res_dir / "root.yaml")
    expected = yaml.safe_load((res_dir / "expected_file.yaml").read_text())
    assert resolved_file.content == expected
