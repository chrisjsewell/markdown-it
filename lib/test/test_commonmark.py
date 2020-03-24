"""In this module tests are run against the full test set,
provided by https://github.com/commonmark/CommonMark.git.
"""
import json
from pathlib import Path

import pytest

from ..main import MarkdownIt

SPEC_INPUT = Path(__file__).parent.joinpath("spec.txt")
TESTS_INPUT = Path(__file__).parent.joinpath("commonmark.json")


def test_against_spec_file(file_regression):
    md = MarkdownIt("working")
    file_regression.check(md.render(SPEC_INPUT.read_text()), extension=".html")


@pytest.mark.parametrize("entry", json.loads(TESTS_INPUT.read_text()))
def test_commonmark(entry):
    md = MarkdownIt("working")
    output = md.render(entry["markdown"])
    assert output == entry["html"]
