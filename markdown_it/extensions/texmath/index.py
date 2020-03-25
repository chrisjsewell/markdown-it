import re
from markdown_it.common.utils import charCodeAt

from markdown_it import MarkdownIt
from markdown_it.utils import AttrDict


def texmath_plugin(md: MarkdownIt, **options):
    delimiters = options.get("delimiters", None) or "dollars"
    macros = options.get("macros", {})

    if delimiters in rules:
        for rule_inline in rules[delimiters]["inline"]:
            md.inline.ruler.before(
                "escape", rule_inline["name"], make_inline_func(rule_inline)
            )

            def render_math_inline(self, tokens, idx, options, env):
                return rule_inline["tmpl"].format(
                    render(tokens[idx].content, False, macros)
                )

            md.add_render_rule(rule_inline["name"], render_math_inline)

        for rule_block in rules[delimiters]["block"]:
            md.block.ruler.before(
                "fence", rule_block["name"], make_block_func(rule_block)
            )

            def render_math_block(self, tokens, idx, options, env):
                return rule_block["tmpl"].format(
                    render(tokens[idx].content, True, macros), tokens[idx].info
                )

            md.add_render_rule(rule_block["name"], render_math_block)


def applyRule(rule, string: str, beg, inBlockquote):

    pre = string.startswith(rule["tag"], beg) and (
        rule["pre"](string, beg) if "pre" in rule else True
    )

    match = rule["rex"].search(string, beg) if pre else False
    post = True
    if match:
        lastIndex = match.end() - 1
        if "post" in rule:
            post = (
                rule["post"](string, lastIndex)  # valid post-condition
                # remove evil blockquote bug (https:#github.com/goessner/mdmath/issues/50)
                and (not inBlockquote or "\n" not in match.group(1))
            )

    return post and match


def make_inline_func(rule):
    def _func(state, silent):
        res = applyRule(rule, state.src, state.pos, False)
        if res:
            if not silent:
                token = state.push(rule["name"], "math", 0)
                token.content = res[1]  # group 1 from regex ..
                token.markup = rule["tag"]

            state.pos = res.end()

        return bool(res)

    return _func


def make_block_func(rule):
    def _func(state, begLine, endLine, silent):
        res = applyRule(
            rule,
            state.src,
            state.bMarks[begLine] + state.tShift[begLine],
            state.parentType == "blockquote",
        )
        if res:
            if not silent:
                token = state.push(rule["name"], "math", 0)
                token.block = True
                token.content = res[1]
                token.info = res[len(res.groups())]
                token.markup = rule["tag"]

            line = begLine
            endpos = res.end() - 1

            while line < endLine:
                if endpos >= state.bMarks[line] and endpos <= state.eMarks[line]:
                    # line for end of block math found ...
                    state.line = line + 1
                    break
                line += 1

            state.pos = res.end()

        return bool(res)

    return _func


def dollar_pre(str, beg):
    prv = charCodeAt(str[beg - 1], 0) if beg > 0 else False
    return (
        (not prv) or prv != 0x5C and (prv < 0x30 or prv > 0x39)  # no backslash,
    )  # no decimal digit .. before opening '$'


def dollar_post(string, end):
    try:
        nxt = string[end + 1] and charCodeAt(string[end + 1], 0)
    except IndexError:
        return True
    return (
        (not nxt) or (nxt < 0x30) or (nxt > 0x39)
    )  # no decimal digit .. after closing '$'


def render(tex, displayMode, macros):
    return tex
    # TODO better render
    # try:
    #     res = katex.renderToString(tex,{throwOnError:False,displayMode,macros})
    # except:
    #     res = tex+": "+err.message.replace("<","&lt;")
    # return res


# def use(katex):  # math renderer used ...
#     texmath.katex = katex;       # ... katex solely at current ...
#     return texmath;
# }


# All regexes areg global (g) and sticky (y), see:
# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp/sticky

rules = AttrDict(
    {
        "brackets": {
            "inline": [
                {
                    "name": "math_inline",
                    "rex": re.compile(r"\\\((.+?)\\\)"),
                    "tmpl": "<eq>{0}</eq>",
                    "tag": "\\(",
                }
            ],
            "block": [
                {
                    "name": "math_block_eqno",
                    "rex": re.compile(
                        r"\\\[(((?!\\\]|\\\[)[\s\S])+?)\\\]\s*?\(([^)$\r\n]+?)\)", re.M
                    ),
                    "tmpl": '<section class="eqno"><eqn>{0}</eqn><span>({1})</span></section>',
                    "tag": "\\[",
                },
                {
                    "name": "math_block",
                    "rex": re.compile(r"\\\[([\s\S]+?)\\\]", re.M),
                    "tmpl": "<section><eqn>{0}</eqn></section>",
                    "tag": "\\[",
                },
            ],
        },
        "gitlab": {
            "inline": [
                {
                    "name": "math_inline",
                    "rex": re.compile(r"\$`(.+?)`\$"),
                    "tmpl": "<eq>{0}</eq>",
                    "tag": "$`",
                }
            ],
            "block": [
                {
                    "name": "math_block_eqno",
                    "rex": re.compile(
                        r"`{3}math\s+?([^`]+?)\s+?`{3}\s*?\(([^)$\r\n]+?)\)", re.M
                    ),
                    "tmpl": '<section class="eqno"><eqn>{0}</eqn><span>({1})</span></section>',
                    "tag": "```math",
                },
                {
                    "name": "math_block",
                    "rex": re.compile(r"`{3}math\s+?([^`]+?)\s+?`{3}", re.M),
                    "tmpl": "<section><eqn>{0}</eqn></section>",
                    "tag": "```math",
                },
            ],
        },
        "julia": {
            "inline": [
                {
                    "name": "math_inline",
                    "rex": re.compile(r"`{2}([^`]+?)`{2}"),
                    "tmpl": "<eq>{0}</eq>",
                    "tag": "``",
                },
                {
                    "name": "math_inline",
                    "rex": re.compile(r"\$(\S[^$\r\n]*?[^\s\\]{1}?)\$"),
                    "tmpl": "<eq>{0}</eq>",
                    "tag": "$",
                    "pre": dollar_pre,
                    "post": dollar_post,
                },
                {
                    "name": "math_single",
                    "rex": re.compile(r"\$([^$\s\\]{1}?)\$"),
                    "tmpl": "<eq>{0}</eq>",
                    "tag": "$",
                    "pre": dollar_pre,
                    "post": dollar_post,
                },
            ],
            "block": [
                {
                    "name": "math_block_eqno",
                    "rex": re.compile(
                        r"`{3}math\s+?([^`]+?)\s+?`{3}\s*?\(([^)$\r\n]+?)\)", re.M
                    ),
                    "tmpl": '<section class="eqno"><eqn>{0}</eqn><span>({1})</span></section>',
                    "tag": "```math",
                },
                {
                    "name": "math_block",
                    "rex": re.compile(r"`{3}math\s+?([^`]+?)\s+?`{3}", re.M),
                    "tmpl": "<section><eqn>{0}</eqn></section>",
                    "tag": "```math",
                },
            ],
        },
        "kramdown": {
            "inline": [
                {
                    "name": "math_inline",
                    "rex": re.compile(r"\${2}([^$\r\n]*?)\${2}"),
                    "tmpl": "<eq>{0}</eq>",
                    "tag": "$$",
                }
            ],
            "block": [
                {
                    "name": "math_block_eqno",
                    "rex": re.compile(r"\${2}([^$]*?)\${2}\s*?\(([^)$\r\n]+?)\)", re.M),
                    "tmpl": '<section class="eqno"><eqn>{0}</eqn><span>({1})</span></section>',
                    "tag": "$$",
                },
                {
                    "name": "math_block",
                    "rex": re.compile(r"\${2}([^$]*?)\${2}", re.M),
                    "tmpl": "<section><eqn>{0}</eqn></section>",
                    "tag": "$$",
                },
            ],
        },
        "dollars": {
            "inline": [
                {
                    "name": "math_inline",
                    "rex": re.compile(r"\$(\S[^$\r\n]*?[^\s\\]{1}?)\$"),
                    "tmpl": "<eq>{0}</eq>",
                    "tag": "$",
                    "pre": dollar_pre,
                    "post": dollar_post,
                },
                {
                    "name": "math_single",
                    "rex": re.compile(r"\$([^$\s\\]{1}?)\$"),
                    "tmpl": "<eq>{0}</eq>",
                    "tag": "$",
                    "pre": dollar_pre,
                    "post": dollar_post,
                },
            ],
            "block": [
                {
                    "name": "math_block_eqno",
                    "rex": re.compile(r"\${2}([^$]*?)\${2}\s*?\(([^)$\r\n]+?)\)", re.M),
                    "tmpl": '<section class="eqno">\n<eqn>{0}</eqn><span>({1})</span>\n</section>\n',
                    "tag": "$$",
                },
                {
                    "name": "math_block",
                    "rex": re.compile(r"\${2}([^$]*?)\${2}", re.M),
                    "tmpl": "<section>\n<eqn>{0}</eqn>\n</section>\n",
                    "tag": "$$",
                },
            ],
        },
    }
)
