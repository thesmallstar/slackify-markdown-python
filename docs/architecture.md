# Architecture

_Last updated: 2026-05-25_

This document explains the moving parts of `slackify-markdown-python` and the
design decisions behind the trickier bits. It assumes you've already read the
README and understand what the library does at a surface level (convert
CommonMark / GFM-flavored Markdown into Slack's `mrkdwn` flavor).

## File layout

```
src/slackify_markdown/
├── __init__.py          # exports `slackify_markdown(text) -> str`
├── service.py           # thin entry: SlackifyMarkdown(text).slackify()
├── slackify.py          # the renderer (everything interesting lives here)
└── utils.py             # escape_specials() — &, <, >, preserves Slack mentions
tests/
└── test_convert.py      # pytest suite
```

## Parsing pipeline

We use `markdown-it-py` as the parser. We extend its `RendererHTML` class and
override the per-token handlers (`paragraph_open`, `bullet_list_close`, etc.)
to emit Slack `mrkdwn` instead of HTML.

```
markdown text
   │
   ▼
slackify()  ── scrub STX from input (see "newline sentinel" below)
   │
   ▼
MarkdownIt(gfm-like).render(text)
   │   produces a flat token stream:
   │   [paragraph_open, inline(text+strong+...), paragraph_close,
   │    bullet_list_open, list_item_open, paragraph_open(hidden), ...,
   │    bullet_list_close]
   ▼
SlackifyMarkdown.render(tokens)
   │   filters to SUPPORTED_TOKENS, then delegates to RendererHTML.render
   │   which dispatches each token to the matching handler method
   │   on our class. Handlers return strings, which are concatenated.
   ▼
post-process: cap structural-newline runs, materialize sentinel → \n, rstrip
   │
   ▼
final mrkdwn string
```

The handlers are mostly straightforward: `strong_open` returns `*`,
`em_open` returns `_`, `link_open/close` build `<url|text>`, etc.

## Format mappings

| Markdown | Slack mrkdwn | Notes |
|---|---|---|
| `# Heading` | `*Heading*` | All 6 levels collapse to Slack's single bold form |
| `**bold**` | `*bold*` | |
| `*italic*` | `_italic_` | |
| `~~strike~~` | `~strike~` | |
| `` `code` `` | `` `code` `` | |
| `[txt](url)` | `<url\|txt>` | |
| `<url>` autolink | `<url\|url>` | |
| `- item` | `•   item` | (4-space indent per nest level) |
| `1. item` | `1.  item` | |
| `> quote` | `> quote` | Single-line prefix; multi-line currently flows as plain |
| Fenced ```` ``` ```` | ```` ``` ```` | Content preserved verbatim, including blank lines |

## The "structural newline" cap and STX sentinel

This is the only nontrivial piece of machinery in the renderer. It exists
because `markdown-it-py`'s default renderer model is a **flat token stream
with string-concatenation**, and that model produces ugly newline cascades
when block elements close in chains.

### The problem

When a deeply nested list ends, several close-handlers fire back-to-back.
Each one independently emits `\n` (or `\n\n`) for "structural separation."
But they don't know about each other. So a 3-level list ending into a
paragraph produces:

```
last_paragraph_close (hidden, tight): \n
inner_list_close:                     \n
mid_list_close:                       \n
outer_list_close:                     \n
                                      = "\n\n\n\n" before next block
```

That's 3 blank lines between the list and the paragraph. Visually broken.

Blockquotes have the same shape: inner `paragraph_close` emits `\n\n`, then
`blockquote_close` adds another `\n` = `\n\n\n` (2 blank lines instead of 1).

### The fix — sentinel + cap regex

We replace every "structural" newline emitted by a close-handler with a
sentinel character `NEW_LINE = "\x02"` (U+0002 STX, ASCII Start of Text).
Then in `render()`, after all handlers have run, we:

1. Cap runs of 3+ sentinels down to 2 with one regex.
2. Replace every sentinel with a real `\n`.

```python
NEW_LINE = "\x02"
_NEW_LINE_CAP_RE = re.compile(NEW_LINE + "{3,}")

def render(self, tokens, options, env):
    final = [t for t in tokens if t.type in self.SUPPORTED_TOKENS]
    rendered = super().render(final, options, env)
    rendered = self._NEW_LINE_CAP_RE.sub(self.NEW_LINE * 2, rendered)
    rendered = rendered.replace(self.NEW_LINE, "\n")
    return rendered.rstrip("\n") + "\n"
```

Net effect: any structural-newline cascade collapses to exactly one blank
line, regardless of how deep the close-chain is.

### Why a sentinel — why not just `re.sub(r"\n{3,}", "\n\n", rendered)`?

Code blocks. A fenced ```` ``` ```` block can legitimately contain runs of
blank lines in its content. If we ran the cap regex against the rendered
output directly, we'd corrupt user code.

By using a sentinel instead of real `\n` for *structural* newlines, we
separate the alphabets:

- Close-handlers emit `\x02` (sentinel) for "I'm contributing to block
  separation"
- Code-block handlers emit literal `\n` for content
- The cap regex only ever sees / cares about runs of `\x02`
- The final `replace` materializes sentinels into real `\n`
- Code-block `\n` is untouched throughout

### Why STX (U+0002) specifically?

This is well-trodden territory. The most-installed Python markdown library,
`python-markdown`, uses **STX (U+0002) and ETX (U+0003)** as boundary
markers for its own internal placeholders (see `markdown/util.py` —
`AMP_SUBSTITUTE`, `INLINE_PLACEHOLDER`, etc.). We use the same convention
for the same reason: STX is an ASCII control character that essentially
never appears in real user text, and is safe to manipulate as a normal
character everywhere we touch it.

Other choices we considered and rejected:

| Choice | Verdict | Why |
|---|---|---|
| `\n{3,}` regex on real newlines | rejected | Eats blank lines inside code blocks |
| Split output on `` ``` ``, regex evens | rejected | Special-casing; readable but ugly |
| `` (Private Use Area) | rejected | "Reserved for cooperating apps to define" — Unicode FAQ explicitly warns this collides with real PUA usage |
| `﷐` (Unicode noncharacter) | rejected | Same valid-Unicode-codepoint risk per FAQ |
| `\x00` NULL | rejected | Python source files cannot contain literal NULL; shells / argv / `os.exec*` all reject NULL |
| **`\x02` STX** | **chosen** | Battle-tested by python-markdown; ASCII-safe in source files, shells, JSON, filesystems |
| Source-level fix (track container state, lookahead, kill cascade at emit) | viable but rejected for now | ~30 lines + new state vs. 1 regex; would couple close-handlers |

### Collision safety — the input scrub

STX *can* appear in user input — `markdown-it-py` does not strip ASCII
control characters during normalization. So before parsing, `slackify()`
runs a one-line scrub:

```python
text = self.markdown_text.replace(self.NEW_LINE, "")
```

This guarantees that no STX reaches the renderer except via our own
close-handlers, so the cap-then-materialize logic can't be confused.

The trade-off: a literal STX a user typed in their Markdown will be
silently dropped. In practice nobody types ASCII control characters into
Markdown by accident, so this is a non-issue.

## State on the renderer

Two pieces of state, both reset to default per-instance:

- `self._in_heading: bool` — set by `heading_open`, cleared by `heading_close`.
  Used by `strong_open/close` to suppress `**` inside `# **Bold**` headings
  (otherwise Slack `mrkdwn` collides: both heading and bold map to `*`,
  producing malformed `**text**` output).
- `self._list_depth: int` — incremented by `bullet_list_open` and
  `ordered_list_open`, decremented by the corresponding closes. Used by
  `list_item_open` to choose the right bullet glyph (`•` / `◦` / `▪` for
  depths 1/2/3+) and to compute the leading indent (`4 * (depth - 1)` spaces).

We never look at sibling/parent token relationships beyond the one-token-back
implicit "did we just see X" via these flags. Anything more sophisticated
would push us toward the AST-walker design (see below).

## Known limitations

These all stem from the same root cause: a flat-token-stream renderer with
no structural context can't compute things that depend on tree shape.

1. **Multi-paragraph items in lists don't carry the list indent.** When a
   list item contains a second paragraph or a code block, the continuation
   block flows back to column 0 instead of being indented to match the
   item. Fixing this needs the renderer to know "I'm currently inside a
   `list_item` at depth N" when handling a `code_block` or non-first
   `paragraph` token.
2. **Hardbreak / softbreak continuation lines inside list items lose
   indent** for the same reason as (1).
3. **Bullet glyphs only have 3 distinct shapes** (`•`, `◦`, `▪`); deeper
   nesting reuses `▪` but indent keeps growing. This matches Slack's own
   native rendering of deeply nested lists.
4. **Multi-line blockquotes** only get the `> ` prefix on the first
   paragraph. Lines after the first `paragraph_close` inside a blockquote
   flow as plain content.

## Would a real AST renderer fix this?

Yes. The cascade is purely an artifact of `markdown-it-py`'s sequential
token-stream renderer model. Each `*_close` handler returns a string in
isolation, and they get concatenated blindly.

A tree-walker renderer would have full structural context: when walking
into a `list_item` node it could push indent state; when emitting the last
child of a top-level `list` node it could emit *exactly* the right
separator for what comes next; multi-paragraph items would naturally
indent because the walker knows it's inside an item.

`markdown-it-py` ships with `markdown_it.tree.SyntaxTreeNode` which can
build a tree from a token list. Migrating would mean writing a recursive
`walk(node) -> str` method that owns its own indent / spacing state,
replacing both the per-handler emit model and the sentinel cap.

This is ~50 lines of refactor and probably the right long-term move. It
would obsolete the sentinel + cap and resolve all four known limitations
above. Not done yet because the current setup works for real Slack
content and the cap is a 5-line fix that buys ~80% of the value.

Tracked in [issue #19](https://github.com/thesmallstar/slackify-markdown-python/issues/19).

## Test coverage

`tests/test_convert.py` contains 60 tests covering:

- All single-token mappings (bold, italic, strike, links, mentions, etc.)
- Tight lists, loose lists, mixed lists, deep nesting up to 5 levels
- Blockquotes with inner content
- Code blocks with special characters and blank-line preservation
- The STX cascade-cap (verified that runs of 3+ blank lines collapse to 1)
- The STX input scrub (verified that user-input STX cannot corrupt output)
- A large "complex_markdown" integration test that exercises most features
  together
- 10 explicitly complex / edge-case tests (deep nesting, mixed ordered/
  unordered, code with specials, loose lists, blockquote+list, all heading
  levels, multi-blank-line collapse-with-code-preservation, link with
  nested formatting, inline-code + mentions, sentinel scrub).

Run with:

```bash
PYTHONPATH=src python3 -m pytest tests/ -v
```
