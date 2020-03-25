import re

from markdown_it import MarkdownIt
from markdown_it.rules_block import StateBlock
from markdown_it.common.utils import charCodeAt, isSpace


PATTERN = re.compile(r"^\{([a-zA-Z\_\-\+\:]{1,36})\}(`+)(?!`)(.+?)(?<!`)\2(?!`)")


def myst_block_plugin(md: MarkdownIt):
    md.block.ruler.before("hr", "myst_block_break", block_break)
    # md.renderer.rules["sphinx_role"] = render_sphinx_role


def block_break(state: StateBlock, startLine: int, endLine: int, silent: bool):

    pos = state.bMarks[startLine] + state.tShift[startLine]
    maximum = state.eMarks[startLine]

    # if it's indented more than 3 spaces, it should be a code block
    if state.sCount[startLine] - state.blkIndent >= 4:
        return False

    marker = charCodeAt(state.src, pos)
    pos += 1

    # Check block marker /* + */:
    if marker != 0x2B:
        return False

    # markers can be mixed with spaces, but there should be at least 3 of them

    cnt = 1
    while pos < maximum:
        ch = charCodeAt(state.src, pos)
        pos += 1
        if ch != marker and not isSpace(ch):
            break
        if ch == marker:
            cnt += 1

    if cnt < 3:
        return False

    if silent:
        return True

    state.line = startLine + 1

    token = state.push("myst-block", "hr", 0)
    token.attrSet("class", "myst-block")
    token.content = state.src[pos:maximum].strip()
    print("hi", token.content)
    token.map = [startLine, state.line]
    token.markup = chr(marker) * (cnt + 1)

    return True
