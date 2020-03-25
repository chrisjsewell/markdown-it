from pathlib import Path

import pytest

from markdown_it import MarkdownIt
from markdown_it.extensions.footnote import footnote_plugin

FIXTURE_PATH = Path(__file__).parent


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


@pytest.mark.parametrize("line,title,input,expected", read_fixture("fixtures"))
def test_all(line, title, input, expected):
    md = MarkdownIt("commonmark").use(footnote_plugin)
    md.options["xhtmlOut"] = False
    text = md.render(input)
    print(text)
    assert text.rstrip().replace("↩︎", "<-").replace(
        "↩", "<-"
    ) == expected.rstrip().replace("↩︎", "<-").replace("↩", "<-")
