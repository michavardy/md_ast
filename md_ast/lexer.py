import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Generator


class TokenType(Enum):
    NEWLINE = auto()


@dataclass
class Token:
    token_type: TokenType
    value: str
    groups: Optional[List[str]] = None


@dataclass
class LexingRule:
    token_type: TokenType
    pattern: Optional[str] = None


lexing_rules = [
    LexingRule(token_type=TokenType.NEWLINE, pattern="\n"),
]


def lex(input_text: str) -> Generator[Token, None, None]:
    seen_simple_text = ""
    while True:
        if len(input_text) == 0:
            if len(seen_simple_text) > 0:
                yield Token(TokenType.TEXT_INLINE, seen_simple_text)
            return
        for rule in lexing_rules:
            match = re.match(rule.pattern, input_text)
            if match is not None:
                matching_rule = rule
                break
        else:
            seen_simple_text += input_text[0]
            input_text = input_text[1:]
            continue  # don't yield a token in this run
        # cut off matched part
        input_text = input_text[len(match[0]):]
        # yield inline text if we have some left
        if len(seen_simple_text) > 0:
            yield Token(TokenType.TEXT_INLINE, seen_simple_text)
            seen_simple_text = ""
        groups = None
        if len(match.groups()) > 0:
            groups = match.groups()
        yield Token(matching_rule.token_type, match[0], groups)


if __name__ == "__main__":
    sample_text = "something\nsomethingelse"
    tokens = lex(sample_text)

