from markdown_it import MarkdownIt
from markdown_it.token import Token
from markdown_it.extensions.sphinx_role import role_plugin


def test_basic():
    md = MarkdownIt().use(role_plugin)
    src = "{abc}``` a ```"
    tokens = md.parse(src)
    print(tokens)
    assert tokens == [
        Token(
            type="paragraph_open",
            tag="p",
            nesting=1,
            attrs=None,
            map=[0, 1],
            level=0,
            children=None,
            content="",
            markup="",
            info="",
            meta=None,
            block=True,
            hidden=False,
        ),
        Token(
            type="inline",
            tag="",
            nesting=0,
            attrs=None,
            map=[0, 1],
            level=1,
            children=[
                Token(
                    type="sphinx_role",
                    tag="",
                    nesting=0,
                    attrs=None,
                    map=None,
                    level=0,
                    children=None,
                    content=" a ",
                    markup="",
                    info="",
                    meta={"name": "abc"},
                    block=False,
                    hidden=False,
                )
            ],
            content="{abc}``` a ```",
            markup="",
            info="",
            meta=None,
            block=True,
            hidden=False,
        ),
        Token(
            type="paragraph_close",
            tag="p",
            nesting=-1,
            attrs=None,
            map=None,
            level=0,
            children=None,
            content="",
            markup="",
            info="",
            meta=None,
            block=True,
            hidden=False,
        ),
    ]
