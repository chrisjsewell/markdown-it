import json
from pathlib import Path

import pytest

from markdown_it import MarkdownIt

FIXTURE_PATH = Path(__file__).parent.joinpath("fixtures")


def read_fixture(name):
    text = FIXTURE_PATH.joinpath(name + ".md").read_text()
    tests = []
    section = 0
    last_pos = 0
    lines = text.splitlines(keepends=True)
    for i in range(len(lines)):
        if lines[i].startswith("."):
            if section == 0:
                tests.append([i, lines[i - 1].strip()])
                section = 1
            elif section == 1:
                tests[-1].append("".join(lines[last_pos + 1 : i]))
                section = 2
            elif section == 2:
                tests[-1].append("".join(lines[last_pos + 1 : i]))
                section = 0

            last_pos = i
    return tests


@pytest.mark.parametrize("line,title,input,expected", read_fixture("tables"))
def test_title(line, title, input, expected):
    md = MarkdownIt("working")
    text = md.render(input)
    assert text.rstrip() == expected.rstrip()


@pytest.mark.parametrize("line, title,input,expected", read_fixture("commonmark_extras"))
def test_commonmark_extras(line, title, input, expected):
    md = MarkdownIt("commonmark")
    text = md.render(input)
    assert text.rstrip() == expected.rstrip()


@pytest.mark.parametrize("line, title,input,expected", read_fixture("fatal"))
def test_fatal(line, title, input, expected):
    md = MarkdownIt("commonmark")
    text = md.render(input)
    assert text.rstrip() == expected.rstrip()
