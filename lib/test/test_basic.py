from ..main import MarkdownIt


def test_basic():
    md = MarkdownIt("working")
    tokens = md.parse("a\n>\n")
    for t in tokens:
        print(t)
        print()
    print(md.render("<!-- a -->"))
    raise
