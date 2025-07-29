import re
import textwrap
from typing import List
from urllib.parse import urlparse

from mistletoe import block_token, span_token, Document
from mistletoe.base_renderer import BaseRenderer
from slackify_markdown.utils import escape_specials


class SlackifyMarkdown(BaseRenderer):
    # ─────────────────────────────────────────────────────────────── #
    # ctor / API
    # ─────────────────────────────────────────────────────────────── #
    def __init__(self, markdown_text: str):
        super().__init__()
        self.markdown_text = textwrap.dedent(markdown_text).lstrip("\n")
        self._list_depth = 0

    def slackify(self) -> str:
        with self:
            return self.render(Document(self.markdown_text))

    # ─────────────────────────────────────────────────────────────── #
    # helpers
    # ─────────────────────────────────────────────────────────────── #
    def _inner(self, tok, sep: str = "") -> str:
        return sep.join(self.render(c) for c in (tok.children or []))

    # ─────────────────────────────────────────────────────────────── #
    # span-level
    # ─────────────────────────────────────────────────────────────── #
    def render_raw_text(self, t):           return escape_specials(t.content)
    def render_strong(self, t):            return f"*{self._inner(t)}*"
    def render_emphasis(self, t):          return f"_{self._inner(t)}_"
    def render_strikethrough(self, t):     return f"~{self._inner(t)}~"
    def render_inline_code(self, t):       return f"`{escape_specials(t.children[0].content)}`"
    def render_line_break(self, _):        return "\n"
    def render_escape_sequence(self, t):   return self._inner(t)

    # ----- links --------------------------------------------------- #
    def render_link(self, t: span_token.Link) -> str:
        label = self._inner(t).strip()
        url   = t.target.strip()
        if not label:                         # []() or reference with blank label
            return f"<{url}>"
        if label == url:                      # angle-bracket auto-link rewritten by parser
            return f"<{url}|{url}>"
        return f"<{url}|{label}>"

    def render_auto_link(self, t: span_token.AutoLink) -> str:
        url = f"mailto:{t.target}" if t.mailto else t.target
        return f"<{url}|{url}>"

    # ----- images -------------------------------------------------- #
    def render_image(self, t: span_token.Image) -> str:
        # alt text is stored in .children (if any) and also .alt
        alt    = (getattr(t, "alt", "") or self._inner(t)).strip()
        title  = (t.title or "").strip(' "\'')
        label  = alt or title
        src    = t.src
        if urlparse(src).scheme:
            return f"<{src}|{label}>" if label else f"<{src}>"
        return label or ""

    # ─────────────────────────────────────────────────────────────── #
    # block-level
    # ─────────────────────────────────────────────────────────────── #
    def render_paragraph(self, t): return f"{self._inner(t)}\n"
    def render_heading(self, t):   return f"*{self._inner(t)}*\n\n"

    # ----- quote --------------------------------------------------- #
    def render_quote(self, t: block_token.Quote) -> str:
     
        output = self._inner(t)
        output = output.strip()

        return "> " + "\n> ".join(output.split("\n")) + "\n"

    # ----- code block --------------------------------------------- #
    def render_block_code(self, t: block_token.BlockCode) -> str:
        if not t.content.strip():
            return ""
        cleaned = re.sub(r"^#!.*?\n", "", t.content)
        return f"```\n{cleaned}```\n"

    # ----- lists --------------------------------------------------- #
    def render_list(self, t: block_token.List) -> str:
        self._list_depth += 1
        out: List[str] = []
        if t.start is None:                          # bullets
            for c in t.children:
                out.append("•   " + self.render(c).rstrip())
        else:                                        # ordered
            n = t.start or 1
            for c in t.children:
                out.append(f"{n}.  " + self.render(c).rstrip())
                n += 1
        root = self._list_depth == 1
        self._list_depth -= 1
        return "\n".join(out) + ("\n" if root else "")

    def render_list_item(self, t): return self._inner(t)

    # ----- misc ---------------------------------------------------- #
    def render_thematic_break(self, _): return "---\n"
    
    def render_table(self, t: block_token.Table) -> str:
        # collect raw cell strings per row
        rows = [[self._inner(c) for c in r.children] for r in t.children]

        # target width for each column: widest cell - then add **one** extra space
        col_w = [max(len(r[i]) for r in rows) + 1 for i in range(len(rows[0]))]

            
    def render_document(self, t):      return self._inner(t)



def slackify_markdown(mrkdown: str) -> str:
    slackify = SlackifyMarkdown(mrkdown)
    return slackify.slackify()