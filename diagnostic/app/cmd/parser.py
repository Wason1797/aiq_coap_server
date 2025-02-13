from collections.abc import Callable
from enum import StrEnum
from functools import partial
from typing import Optional


class Token(StrEnum):
    ID = "id:"
    RLOC16 = "rloc16:"
    SPACE = " "
    EXT_ADDR = "ext-addr:"
    VER = "ver:"
    DASH = "-"
    ME = "me"
    LEADER = "leader"
    BR = "br"
    LINKS_3 = "3-links:"
    LINKS_2 = "2-links:"
    LINKS_1 = "1-links:"
    OPEN_CURLY = "{"
    CLOSE_CURLY = "}"
    NEW_LINE = "\n"
    DONE = "Done"


def consume(_: str):
    return 0, ""


def consume_until_token(remainder: str, token: str = Token.SPACE) -> tuple[int, str]:
    for index, char in enumerate(remainder):
        if char == token:
            return index, remainder[:index].rstrip(token)
    return 0, ""


def consume_links(remainder: str, token: str) -> tuple[int, str]:
    index, result = consume_until_token(remainder, token)
    return index, result.lstrip(Token.OPEN_CURLY).strip()


def consume_dash(remainder: str) -> tuple[int, str]:
    for index, char in enumerate(remainder):
        if char == Token.DASH:
            if remainder[index + 1 if index < len(remainder) + 1 else index] in {
                Token.SPACE,
                Token.DASH,
                Token.NEW_LINE,
            }:
                return index, remainder[:index]
            else:
                return 0, ""
        elif char == Token.NEW_LINE:
            return index, remainder[:index]
    return 0, ""


TOKENS: dict[Token | str, Callable[[str], tuple[int, str]]] = {
    Token.ID: consume_until_token,
    Token.RLOC16: consume_until_token,
    Token.SPACE: consume,
    Token.DASH: consume_dash,
    Token.EXT_ADDR: consume_until_token,
    Token.VER: consume_until_token,
    Token.LINKS_3: partial(consume_links, token=Token.CLOSE_CURLY),
    Token.LINKS_2: partial(consume_links, token=Token.CLOSE_CURLY),
    Token.LINKS_1: partial(consume_links, token=Token.CLOSE_CURLY),
    Token.OPEN_CURLY: consume,
    Token.CLOSE_CURLY: consume,
    Token.NEW_LINE: consume,
    Token.DONE: consume,
}


class Node:
    def __init__(
        self,
        id: str,
    ):
        self.id = id
        self.rloc16: Optional[str] = None
        self.ext_addr: Optional[str] = None
        self.ver: Optional[str] = None
        self.extras: list[str] = []
        self.links: list[tuple[str, int]] = []

    def __repr__(self) -> str:
        return f"Node {self.id} rloc16: {self.rloc16} ext: {self.ext_addr} ver: {self.ver}"


def parse_meshdiag_topology_string(meshdiag_topology: str) -> list[tuple[str, str]]:
    parsed_tokens: list[tuple[str, str]] = []
    start, end = 0, 1

    while end < len(meshdiag_topology):
        current_token = meshdiag_topology[start:end]

        if action := TOKENS.get(current_token):
            offset, result = action(meshdiag_topology[end:])
            if current_token and result:
                parsed_tokens.append((current_token, result))
            start = end + offset
            end = start + 1
        else:
            end += 1

    return parsed_tokens


def convert_parsed_tokens_into_nodes(parsed_tokens: list[tuple[str, str]]) -> list[Node]:
    current_node: Optional[Node] = None
    nodes: list[Node] = []
    for token, value in parsed_tokens:
        match token:
            case Token.ID:
                current_node = Node(id=value)
                nodes.append(current_node)
            case Token.LINKS_3 if current_node:
                current_node.links.extend((id, 3) for id in value.split())
            case Token.LINKS_2 if current_node:
                current_node.links.extend((id, 2) for id in value.split())
            case Token.LINKS_1 if current_node:
                current_node.links.extend((id, 1) for id in value.split())
            case Token.DASH if current_node:
                current_node.extras.append(value.strip())
            case _ if current_node:
                setattr(
                    current_node,
                    token.strip(":").replace("-", "_"),
                    value.strip(Token.NEW_LINE),
                )
    return nodes


def make_serializable_graph(nodes: list[Node]) -> dict:
    graph = {
        "nodes": [],
        "edges": [],
    }

    for node in nodes:
        graph["nodes"].append(
            {
                "id": node.id,
                "title": node.rloc16,
                "subtitle": node.ext_addr,
                "mainstat": node.ver,
                "secondary_stat": "",
                "color": "blue" if Token.BR in node.extras else "green",
                "highlighted": Token.ME in node.extras,
            }
        )

        for idx, link in enumerate(node.links):
            target, quality = link
            graph["edges"].append(
                {"id": f"node_{node.id}_link_{idx+1}", "source": node.id, "target": target, "thickness": quality, "color": "orange"}
            )

    return graph
