import re
from pathlib import Path
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Generator


@dataclass
class Token:
    token_type: TokenType
    value: str
    groups: Optional[List[str]] = None

@dataclass
class LexingRule:
    token_type: TokenType
    pattern: Optional[str] = None

# noinspection PyArgumentList
class TokenType(Enum):
    TEXT_INLINE = 1
    NEWLINE = auto()
    TITLE_1 = auto()
    TITLE_2 = auto()
    TITLE_3 = auto()
    TITLE_4 = auto()
    TITLE_5 = auto()
    TITLE_6 = auto()
    CODE_BLOCK = auto()
    DEFINITION = auto()
    LIST_1 = auto()
    LIST_2 = auto()
    LIST_3 = auto()
    LIST_4 = auto()
    LIST_5 = auto()
    LIST_6 = auto()
    PICTURE = auto()


lexing_rules = [
    LexingRule(token_type=TokenType.NEWLINE, pattern="\n"),
    LexingRule(token_type=TokenType.TITLE_1, pattern=r"(^\#\s)([a-zA-Z]+)"),
    LexingRule(token_type=TokenType.TITLE_2, pattern=r"(^\#\#\s)([a-zA-Z]+)"),
    LexingRule(token_type=TokenType.TITLE_3, pattern=r"(^\#\#\#\s)([a-zA-Z]+)"),
    LexingRule(token_type=TokenType.TITLE_4, pattern=r"(^\#\#\#\#\s)([a-zA-Z]+)"),
    LexingRule(token_type=TokenType.TITLE_5, pattern=r"(^\#\#\#\#\#\s)([a-zA-Z]+)"),
    LexingRule(token_type=TokenType.TITLE_6, pattern=r"(^\#\#\#\#\#\#\s)([a-zA-Z]+)"),
    LexingRule(token_type=TokenType.CODE_BLOCK, pattern=r"\`\`\`"),
    LexingRule(token_type=TokenType.DEFINITION, pattern=r"(\:\s)(.*)"),
    LexingRule(token_type=TokenType.LIST_1, pattern=r"(^\-\s)(.*)"),
    LexingRule(token_type=TokenType.LIST_2, pattern=r"(^\s{3}\-\s)(.*)"),
    LexingRule(token_type=TokenType.LIST_3, pattern=r"(^\s{5}\-\s)(.*)"),
    LexingRule(token_type=TokenType.LIST_4, pattern=r"(^\s{7}\-\s)(.*)"),
    LexingRule(token_type=TokenType.LIST_5, pattern=r"(^\s{9}\-\s)(.*)"),
    LexingRule(token_type=TokenType.LIST_6, pattern=r"(^\s{11}\-\s)(.*)"),
    LexingRule(token_type=TokenType.PICTURE, pattern=r"\!(\[.*\])(\(.*\))")
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
    sample_text = Path('./md_ast/md_ast/example1.md').read_text()
    tokens = lex(sample_text)


