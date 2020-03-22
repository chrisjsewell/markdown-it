""" Atex heading (#, ##, ...) """

from .state_block import StateBlock

from ..common.utils import isSpace, charCodeAt


def heading(state: StateBlock, startLine: int, endLine: int, silent: bool):
    pos = state.bMarks[startLine] + state.tShift[startLine]
    maximum = state.eMarks[startLine]

    # if it's indented more than 3 spaces, it should be a code block
    if state.sCount[startLine] - state.blkIndent >= 4:
        return False

    ch = charCodeAt(state.src, pos)

    # /* # */
    if ch != 0x23 or pos >= maximum:
        return False

    # count heading level
    level = 1
    pos += 1
    ch = charCodeAt(state.src, pos)
    # /* # */
    while ch == 0x23 and pos < maximum and level <= 6:
        level += 1
        pos += 1
        ch = charCodeAt(state.src, pos)

    if level > 6 or (pos < maximum and not isSpace(ch)):
        return False

    if silent:
        return True

    # Let's cut tails like '    ###  ' from the end of string

    maximum = state.skipSpacesBack(maximum, pos)
    tmp = state.skipCharsBack(maximum, 0x23, pos)  # #
    if tmp > pos and isSpace(charCodeAt(state.src, tmp - 1)):
        maximum = tmp

    state.line = startLine + 1

    token = state.push("heading_open", "h" + str(level), 1)
    token.markup = "########"[:level]
    token.map = [startLine, state.line]

    token = state.push("inline", "", 0)
    token.content = state.src[pos:maximum].strip()
    token.map = [startLine, state.line]
    token.children = []

    token = state.push("heading_close", "h" + str(level), -1)
    token.markup = "########"[:level]

    return True
