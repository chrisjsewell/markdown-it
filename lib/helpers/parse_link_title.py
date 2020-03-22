"""Parse link title
"""

from ..common.utils import unescapeAll, charCodeAt


class _Result:
    __slots__ = ("ok", "pos", "lines", "string")

    def __init__(self):
        self.ok = False
        self.pos = 0
        self.lines = 0
        self.string = ""


def parseLinkTitle(string, pos, maximum):
    lines = 0
    start = pos
    result = _Result()

    if pos >= maximum:
        return result

    marker = charCodeAt(string, pos)

    # /* " */  /* ' */  /* ( */
    if marker != 0x22 and marker != 0x27 and marker != 0x28:
        return result

    pos += 1

    # if opening marker is "(", switch it to closing marker ")"
    if marker == 0x28:
        marker = 0x29

    while pos < maximum:
        code = charCodeAt(string, pos)
        if code == marker:
            result.pos = pos + 1
            result.lines = lines
            result.string = unescapeAll(string[start + 1, pos])
            result.ok = True
            return result
        elif code == 0x0A:
            lines += 1
        elif code == 0x5C and pos + 1 < maximum:  # /* \ */
            pos += 1
            if string.charCodeAt(pos) == 0x0A:
                lines += 1

        pos += 1

    return result
