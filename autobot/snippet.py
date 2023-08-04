from __future__ import annotations

import ast
import re
from typing import Generator, NamedTuple, Type


class Snippet(NamedTuple):
    """A snippet extracted from source code."""

    text: str
    padding: str
    lineno: int

    @classmethod
    def from_node(cls, source_code: str, node: ast.AST) -> Snippet:
        return decontextualize(source_code, node)


def decontextualize(source_code: str, node: ast.AST) -> Snippet:
    """Decontextualize a snippet from its originating source code.

    Takes the originating source code as input, along with the node to decontextualize,
    and extracts the code as a snippet, removing any indentation.
    """
    # Extract the source segment.
    source_segment = ast.get_source_segment(source_code, node, padded=True)
    assert source_segment, "Unable to find source segment."

    # Dedent the code:.
    # TODO(charlie): This isn't safe. For example, there could be multi-line strings
    # within a function that need this padding.
    lines = source_segment.splitlines()
    if m := re.match(r"(\s+)", lines[0]):
        padding = m.group()
        source_segment = "\n".join([line.removeprefix(padding) for line in lines])
    else:
        padding = ""

    return Snippet(source_segment, padding, node.lineno)


def recontextualize(snippet: Snippet, source_code: str) -> list[str]:
    """Recontextualize a snippet within its originating source code.

    Takes the originating source code and snippet as input, and outputs the lines of the
    source code up to and including the snippet, with the snippet adjusted to match the
    indentation of its originating context.
    """
    lines: list[str] = []

    if snippet.lineno > 1:
        # Prepend any lines of the originating source code that precede the snippet.
        source_lines = source_code.splitlines()
        lines.extend(source_lines[i] for i in range(snippet.lineno - 1))
    # Tack on the snippet itself, with indentation re-applied.
    lines.extend(snippet.padding + line for line in snippet.text.splitlines())
    return lines


def iter_snippets(
    source_code: str,
    node_type: Type[ast.AST] | tuple[Type[ast.AST], ...],
) -> Generator[Snippet, None, None]:
    """Generate all snippets from the provided source code.

    Returns: a tuple of (text to fix, any indentation that was removed from the
        snippet, line number in the source file).
    """
    for node in ast.walk(ast.parse(source_code)):
        if isinstance(node, node_type):
            yield Snippet.from_node(source_code, node)
