# Clean up tokens after emphasis and strikethrough postprocessing:
# merge adjacent text nodes into one and re-calculate all token levels
#
# This is necessary because initially emphasis delimiter markers (*, _, ~)
# are treated as their own separate text tokens. Then emphasis rule either
# leaves them as text (needed to merge with adjacent text) or turns them
# into opening/closing tags (which messes up levels inside).
#
from .state_inline import StateInline


def text_collapse(state: StateInline, *args):

    level = 0
    tokens = state.tokens
    maximum = len(state.tokens)

    curr = last = 0
    while curr < maximum:
        # re-calculate levels after emphasis/strikethrough turns some text nodes
        # into opening/closing tags
        if tokens[curr].nesting < 0:
            level -= 1  # closing tag
        tokens[curr].level = level
        if tokens[curr].nesting > 0:
            level += 1  # opening tag

        if (
            tokens[curr].type == "text"
            and curr + 1 < maximum
            and tokens[curr + 1].type == "text"
        ):
            # collapse two adjacent text nodes
            tokens[curr + 1].content = tokens[curr].content + tokens[curr + 1].content
        else:
            if curr != last:
                tokens[last] = tokens[curr]

            last += 1
        curr += 1

    # if curr != last:
    #     tokens.length = last
