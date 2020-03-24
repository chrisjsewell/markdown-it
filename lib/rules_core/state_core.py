from typing import List

from ..token import Token
from ..ruler import StateBase


class Tokens(list):
    pass
    # def append(self, token):
    #     raise
    #     super().append(token)


class StateCore(StateBase):
    def __init__(self, src: str, md, env):
        self.src = src
        self.md = md  # link to parser instance
        self.env = env
        self.tokens: List[Token] = Tokens()
        self.inlineMode = False
