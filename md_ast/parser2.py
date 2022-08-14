import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Generator, Any, List, Dict, Tuple, Iterable

from md_ast.lexer import Token, TokenType


# noinspection PyArgumentList
class NodeType(Enum):
    TITLE = auto()
    CODE_BLOCK = auto()
    DEFINITION = auto()
    LIST = auto()
    PICTURE = auto()


@dataclass
class Node:
    node_type: NodeType
    text_content: Optional[str] = None
    children: Optional[Generator] = None

def merge_text_nodes(subTree: Iterable[Node]) -> Generator :

