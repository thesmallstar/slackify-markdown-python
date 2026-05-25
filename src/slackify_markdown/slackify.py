from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token
from typing import List, Dict, Any
import re
from urllib.parse import urlparse
from slackify_markdown.utils import escape_specials


# Todo: Clean code before release.
class SlackifyMarkdown(RendererHTML):

    SUPPORTED_TOKENS = [
        "text",
        "inline",
        "strong_open",
        "strong_close",
        "em_open",
        "em_close",
        "s_open",
        "s_close",
        "link_open",
        "link_close",
        "code_inline",
        "code_block",
        "bullet_list_open",
        "bullet_list_close",
        "ordered_list_open",
        "ordered_list_close",
        "list_item_open",
        "list_item_close",
        "paragraph_open",
        "paragraph_close",
        "blockquote_open",
        "blockquote_close",
        "image",
        "heading_open",
        "heading_close",
        "fence",
        "table_open",
        "table_close",
        "td_open",
        "td_close",
        "th_open",
        "th_close",
        "tr_open",
        "tr_close",
        "hardbreak",
        "softbreak",
    ]

    _BULLETS_BY_DEPTH = ("•", "◦", "▪")
    _INDENT_UNIT = "    "
    # U+0002 STX (Start of Text) is the "structural newline" sentinel.
    # Close-handlers emit this instead of "\n" so render() can cap structural-
    # newline runs at 2 (one blank line) without touching real \n inside code
    # blocks. Same approach python-markdown uses for its placeholders.
    # User input is scrubbed of NEW_LINE in slackify() so collisions are
    # impossible. See architecture.md for the full rationale.
    NEW_LINE = "\x02"
    _NEW_LINE_CAP_RE = re.compile(NEW_LINE + "{3,}")

    def __init__(self, markdown_text: str):
        super().__init__()
        self.markdown_text = markdown_text
        self._in_heading = False
        self._list_depth = 0

    # this is not correctly done, we need to check in an depth for children,
    # the library offers allowed tokens/tags. Move to that instead of this :), todo.
    def render(
        self, tokens: List[Token], options: Dict[str, Any], env: Dict[str, Any]
    ) -> str:
        final_tokens = []
        for token in tokens:
            if token.type in self.SUPPORTED_TOKENS:
                final_tokens.append(token)

        rendered = super().render(final_tokens, options, env)
        # Cap structural-newline runs at 2 (one blank line), then materialize
        # to real \n. Code blocks emit real \n directly, so their content is
        # not affected by the cap.
        rendered = self._NEW_LINE_CAP_RE.sub(self.NEW_LINE * 2, rendered)
        rendered = rendered.replace(self.NEW_LINE, "\n")
        return rendered.rstrip("\n") + "\n"

    def hardbreak(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        return "\n"

    def softbreak(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        return "\n"

    def slackify(self) -> str:
        # Scrub the sentinel char from user input so it can't collide with our
        # newline-cap machinery in render(). markdown-it-py does not strip
        # ASCII control chars, so we have to do it here.
        text = self.markdown_text.replace(self.NEW_LINE, "")
        md = MarkdownIt(
            "gfm-like",
            renderer_cls=type(self),
            options_update={
                "html": False,
                "linkify": False,
                "breaks": False,
            },
        ).disable("table")

        return md.render(text)

    def text(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        return escape_specials(tokens[idx].content)

    def heading_open(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        self._in_heading = True
        return "*"

    def heading_close(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        self._in_heading = False
        return f"*{self.NEW_LINE}{self.NEW_LINE}"

    def strong_open(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        if self._in_heading:
            return ""
        return "*"

    def strong_close(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        if self._in_heading:
            return ""
        return "*"

    def em_open(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        return "_"

    def em_close(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        return "_"

    def s_open(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        return "~"

    def s_close(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        return "~"

    def link_open(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        href = tokens[idx].attrs.get("href", "")
        only_link = False
        if tokens[idx + 1].nesting == -1:
            only_link = True

        if only_link:
            return f"<{href}"
        else:
            return f"<{href}|"

    def link_close(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        content = tokens[idx].content

        if content:
            return f">: {content}\n"
        else:
            return ">"

    def code_inline(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        content = tokens[idx].content
        return f"`{content}`"

    def code_block(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        content = tokens[idx].content
        # Remove deprecated language declarations (lines starting with #!)
        content = re.sub(r"^#!.*?\n", "", content)
        return f"```\n{content}```\n"

    def fence(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        content = tokens[idx].content
        # Remove deprecated language declarations (lines starting with #!)
        content = re.sub(r"^#!.*?\n", "", content)
        return f"```\n{content}```\n"

    def bullet_list_open(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        self._list_depth += 1
        return ""

    def bullet_list_close(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        self._list_depth -= 1
        return self.NEW_LINE

    def list_item_open(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        indent = self._INDENT_UNIT * max(self._list_depth - 1, 0)
        if tokens[idx].info:
            return f"{indent}{tokens[idx].info}.  "
        depth_idx = min(max(self._list_depth - 1, 0), len(self._BULLETS_BY_DEPTH) - 1)
        return f"{indent}{self._BULLETS_BY_DEPTH[depth_idx]}   "

    def list_item_close(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        return ""

    def ordered_list_open(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        self._list_depth += 1
        return ""

    def ordered_list_close(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        self._list_depth -= 1
        return self.NEW_LINE

    def paragraph_open(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        return ""

    def paragraph_close(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        # Tight-list items have hidden paragraph tokens; they only need a
        # single newline between items, not a blank-line block separator.
        if tokens[idx].hidden:
            return self.NEW_LINE
        return f"{self.NEW_LINE}{self.NEW_LINE}"

    def blockquote_open(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        return "> "

    def blockquote_close(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        return self.NEW_LINE

    def image(
        self,
        tokens: List[Token],
        idx: int,
        options: Dict[str, Any],
        env: Dict[str, Any],
    ) -> str:
        src = tokens[idx].attrs.get("src", "")
        title = tokens[idx].attrs.get("title", "")
        display_text = tokens[idx].content or title

        parsed_url = urlparse(src)

        if parsed_url.scheme and parsed_url.netloc:
            output = "<" + src
            if display_text:
                output += "|" + display_text
            output += ">"
            return output
        else:
            return display_text
