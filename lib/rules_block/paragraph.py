"""Paragraph."""
from typing import List

from ..ruler import Ruler
from .state_block import StateBlock


def paragraph(state: StateBlock, startLine: int, endLine: int, silent: bool = False):

    nextLine = startLine + 1
    ruler: Ruler = state.md.block.ruler
    terminatorRules = ruler.getRules("paragraph")
    endLine = state.lineMax

    oldParentType = state.parentType
    state.parentType = "paragraph"

    # jump line-by-line until empty one or EOF
    while nextLine < endLine:
        if state.isEmpty(nextLine):
            break
        # this would be a code block normally, but after paragraph
        # it's considered a lazy continuation regardless of what's there
        if state.sCount[nextLine] - state.blkIndent > 3:
            nextLine += 1
            continue

        # quirk for blockquotes, this line should already be checked by that rule
        if state.sCount[nextLine] < 0:
            nextLine += 1
            continue

        # Some tags can terminate paragraph without empty line.
        terminate = False
        for terminatorRule in terminatorRules:
            if terminatorRule(state, nextLine, endLine, True):
                terminate = True
                break

        if terminate:
            break

        nextLine += 1

    content = state.getLines(startLine, nextLine, state.blkIndent, False).strip()

    state.line = nextLine

    token = state.push("paragraph_open", "p", 1)
    token.map = [startLine, state.line]

    token = state.push("inline", "", 0)
    token.content = content
    token.map = [startLine, state.line]
    token.children = []

    token = state.push("paragraph_close", "p", -1)

    state.parentType = oldParentType

    return True
