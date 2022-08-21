import regex as re
from pathlib import Path
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Generator, Any, List, Dict, Tuple, Iterable
'''
TODO: 
    I should merge to master, upload github
    start building applications like pdf builder    
'''

@dataclass
class Token:
    token_type: str
    value: str
    span: tuple[int]
    match: re.Match
    token_types = [
        'TEXT_INLINE', 'NEWLINE', 'TITLE', 'CODEBLOCK',
        'DEFINITION', 'LIST', 'PICTURE']
    hierarchy: Optional[int] = 1
    keyword_group: Optional[int] = None
    keyword: Optional[str] = None


@dataclass
class LexingRule:
    token_type: str
    pattern: Optional[str] = None
    hierarchyGroup: Optional[int] = None
    hierarchyCount: Optional[str] = None
    valueGroup: Optional[int] = None
    hierarchy: Optional[str] = None
    pair: bool = False
    keyword_group: Optional[int] = None


@dataclass
class Node:
    # a node is a sequence of tokens
    node_types = ['Title', 'CODE_BLOCK', 'DEFINITION', 'LIST', 'PICTURE']
    node_type: str
    token_type_seq: list[str]
    value: Optional[Token] = None
    value_order: Optional[int] = None
    keyword: Optional[Token] = None
    keyword_order: Optional[int] = None
    hierarchy: Optional[int] = None
    group: Optional[list] = None


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.lexing_rules = [
            #LexingRule(token_type='NEWLINE', pattern="\n"),
            LexingRule(token_type='TITLE', pattern=r"(\#+)\s([0-9a-zA-Z ]+)", valueGroup=1, hierarchyGroup=0, hierarchyCount='#'),
            LexingRule(token_type='CODE_BLOCK', pattern=r"\`{3}([0-9a-zA-Z \n().*'\"]*)\`{3}", valueGroup=0),
            LexingRule(token_type='DEFINITION', pattern=r"(\n[0-9a-zA-Z(). ']+)\n\:(\s[0-9a-zA-Z(). ']+)", valueGroup=1, keyword_group=0),
            LexingRule(token_type='LIST', pattern=r"(\s*\-\s)(.*)", valueGroup=1, hierarchyGroup=0, hierarchyCount='  '),
            LexingRule(token_type='PICTURE', pattern=r"\!(\[.*\])(\(.*\))", valueGroup=1),
            LexingRule(token_type='INLINE_TEXT', pattern="\n[0-9a-zA-Z(). ']+", valueGroup=0),
            LexingRule(token_type='NEWLINE', pattern="\n", valueGroup=0),
        ]
        self.tokens = self.lex_nonConsume(self.text)
        self.post_process()

    def extract_token_from_match(self, match: re.Match, rule: LexingRule) -> Token:
        token_type = rule.token_type
        hierarchy = None
        keyword = None
        span = match.span()
        #span_match = re.search(match.group(), self.text)
        if rule.valueGroup:
            value = match.groups()[rule.valueGroup]
        else:
            value = match.group()
        #if span_match:
        #    span = span_match.span()
        if rule.hierarchyGroup is not None:
            hierarchy = match.groups()[rule.hierarchyGroup].count(rule.hierarchyCount) + 1
        if rule.keyword_group is not None:
            keyword = match.groups()[rule.keyword_group]
        token = Token(token_type=token_type, value=value, match=match, hierarchy=hierarchy, keyword=keyword, span=span)
        return token

    def lex(self, input_text: str) -> list:
        '''
            I have tried using re.finditer without trimming the input text,
            but I can't max consequitve lines like \n text \n text2 \n
            because it overlaps, I will be reverting back to deleting the input text
            it will also probebly be faster
        '''
        text = input_text
        token_lst = []
        # loop 1
        while True:
            # loop 2: iterate over rules
            for index, rule in enumerate(self.lexing_rules):
                # all matches in input text
                match = re.search(rule.pattern, text)
                if (match is not None) and (match not in [t.match for t in token_lst]):
                    # add token to token list
                    token_lst.append(self.extract_token_from_match(match, rule))
                    # remove text
                    text = text[:match.start()] + text[match.end():]
                    # break loop 2
                    break
            # if loop2 has completed without match
            else:
                return(token_lst)

    def lex_nonConsume(self, input_text: str) -> list:
        '''
            I have tried using re.finditer without trimming the input text,
            but I can't max consequitve lines like \n text \n text2 \n
            because it overlaps, I will be reverting back to deleting the input text
            it will also probebly be faster
        '''
        text = input_text
        token_lst = []
        # loop 1: iterate over rules
        for index, rule in enumerate(self.lexing_rules):
            # all matches in input text
            match_list = re.finditer(rule.pattern, text)
            for match in match_list:
                if (match is not None) and (match not in [t.match for t in token_lst]):
                    # add token to token list
                    token_lst.append(self.extract_token_from_match(match, rule))
        return(token_lst)

    def clean_tokens(self):
        # clean up value
        new_tokens = []
        # iterate over tokens
        for token in self.tokens:
            # remove newlines in tokens
            token.value = re.sub('\n', ' ', token.value)
            # strip text
            token.value = token.value.strip()
            # append new tokens
            new_tokens.append(token)
        self.tokens = new_tokens

    def post_process(self):
        # remove newline tokens
        self.tokens = [t for t in self.tokens if t.token_type!='NEWLINE']
        # clean tokens
        self.clean_tokens()
        # sort tokens
        self.tokens.sort(key=lambda t: t.span[0])


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens


if __name__ == "__main__":
    sample_text = Path('./md_ast/md_ast/example1.md').read_text()
    lex = Lexer(sample_text)
    tokens = lex.tokens
    parse = Parser(tokens)