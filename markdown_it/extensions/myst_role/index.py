import re

from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline
from markdown_it.common.utils import charCodeAt


PATTERN = re.compile(r"^\{([a-zA-Z\_\-\+\:]{1,36})\}(`+)(?!`)(.+?)(?<!`)\2(?!`)")


def role_plugin(md: MarkdownIt):
    md.inline.ruler.before("backticks", "sphinx_role", sphinx_role)
    md.renderer.rules["sphinx_role"] = render_sphinx_role


def sphinx_role(state: StateInline, silent: bool):
    try:
        if charCodeAt(state.src, state.pos - 1) == 0x5C:  # /* \ */
            # escaped (this could be improved in the case of edge case '\\{')
            return False
    except IndexError:
        pass

    match = PATTERN.search(state.src[state.pos :])
    if not match:
        return False
    state.pos += match.end()

    if not silent:
        token = state.push("sphinx_role", "", 0)
        token.meta = {"name": match.group(1)}
        token.content = match.group(3)

    return True


def render_sphinx_role(self, tokens, idx, options, env):
    token = tokens[idx]
    name = token.meta.get("name", "unknown")
    return (
        '<code class="sphinx-role">'
        f"{{{name}}}[{token.content}]"
        "</code>"
    )
