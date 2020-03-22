from typing import List, Optional, Tuple

import attr


@attr.s(slots=True)
class Token:
    # Type of the token (string, e.g. "paragraph_open")
    type: str = attr.ib()
    # html tag name, e.g. "p"
    tag: str = attr.ib()
    # Level change (number in {-1, 0, 1} set), where:
    # -  `1` means the tag is opening
    # -  `0` means the tag is self-closing
    # - `-1` means the tag is closing
    nesting: int = attr.ib()
    # Html attributes. Format: `[ [ name1, value1 ], [ name2, value2 ] ]`
    attrs: Optional[list] = attr.ib(default=None)
    # Source map info. Format: `[ line_begin, line_end ]`
    map: Optional[Tuple[int, int]] = attr.ib(default=None)
    # nesting level, the same as `state.level`
    level: int = attr.ib(default=0)
    # An array of child nodes (inline and img tokens)
    children: Optional[List["Token"]] = attr.ib(default=None)
    # In a case of self-closing tag (code, html, fence, etc.),
    # it has contents of this tag.
    content: str = attr.ib(default="")
    # '*' or '_' for emphasis, fence string for fence, etc.
    markup: str = attr.ib(default="")
    # fence infostring
    info: str = attr.ib(default="")
    # A place for plugins to store an arbitrary data
    meta: Optional[dict] = attr.ib(default=None)
    # True for block-level tokens, false for inline tokens.
    # Used in renderer to calculate line breaks
    block: bool = attr.ib(default=False)
    # If it's true, ignore this element when rendering.
    # Used for tight lists to hide paragraphs.
    hidden: bool = attr.ib(default=False)

    def attrIndex(self, name: str) -> int:
        if not self.attrs:
            return -1
        for i, at in enumerate(self.attrs):
            if at[0] == name:
                return i
        return -1

    def attrPush(self, attrData: Tuple[str, str]):
        """Add `[ name, value ]` attribute to list. Init attrs if necessary."""
        if self.attrs:
            self.attrs.append(attrData)
        else:
            self.attrs = [attrData]

    def attrSet(self, name: str, value: str):
        """Set `name` attribute to `value`. Override old value if exists."""
        idx = self.attrIndex(name)
        if idx < 0:
            self.attrPush([name, value])
        else:
            self.attrs[idx] = [name, value]

    def attrGet(self, name: str) -> str:
        """ Get the value of attribute `name`, or null if it does not exist."""
        idx = self.attrIndex(name)
        if idx >= 0:
            return self.attrs[idx][1]
        return None

    def attrJoin(self, name, value):
        """Join value to existing attribute via space.
        Or create new attribute if not exists.
        Useful to operate with token classes.
        """
        idx = self.attrIndex(name)
        if idx < 0:
            self.attrPush([name, value])
        else:
            self.attrs[idx][1] = self.attrs[idx][1] + ' ' + value

    def as_dict(self, children=True, filter=None, dict_factory=dict):
        """Return the token as a dict.

        :param bool children: Also convert children to dicts
        :param callable filter: A callable whose return code determines whether an
            attribute or element is included (``True``) or dropped (``False``).  Is
            called with the `attr.Attribute` as the first argument and the
            value as the second argument.
        :param callable dict_factory: A callable to produce dictionaries from.  For
            example, to produce ordered dictionaries instead of normal Python
            dictionaries, pass in ``collections.OrderedDict``.

        """
        return attr.asdict(self, recurse=children, filter=filter, dict_factory=dict_factory)
