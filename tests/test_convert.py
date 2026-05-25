from slackify_markdown import slackify_markdown


def test_combined_formatting():
    markdown = "**Bold** and _Italic_ with `inline code`."
    expected = "*Bold* and _Italic_ with `inline code`.\n"
    assert slackify_markdown(markdown) == expected


def test_escaped_characters():
    markdown = "Use & to join, <tag>, and >symbol<."
    expected = "Use &amp; to join, &lt;tag&gt;, and &gt;symbol&lt;.\n"
    assert slackify_markdown(markdown) == expected


def test_mentions():
    markdown = "<@U12345>"
    expected = "<@U12345>\n"
    assert slackify_markdown(markdown) == expected


def test_channel_links():
    markdown = "<#C12345|general>"
    expected = "<#C12345|general>\n"
    assert slackify_markdown(markdown) == expected


def test_user_group_mentions():
    markdown = "<!subteam^S12345|team>"
    expected = "<!subteam^S12345|team>\n"
    assert slackify_markdown(markdown) == expected


def test_bold_italics_strike_bullet_list():
    markdown = "- **Bold** and _Italic_ with ~~strike~~.\n\n- **Bold** and _Italic_ with ~~strike~~.\n\n"
    expected = "•   *Bold* and _Italic_ with ~strike~.\n\n•   *Bold* and _Italic_ with ~strike~.\n"
    assert slackify_markdown(markdown) == expected


def test_bold_italics_strike_ordered_list():
    markdown = "1. **Bold** and _Italic_ with ~~strike~~.\n\n2. **Bold** and _Italic_ with ~~strike~~.\n\n"
    expected = "1.  *Bold* and _Italic_ with ~strike~.\n\n2.  *Bold* and _Italic_ with ~strike~.\n"
    assert slackify_markdown(markdown) == expected


def test_bold_italics_strike_multiline():
    markdown = """
**~~_AP-238: New Task for AP Project_~~**
**~~_AP-222: Citations_~~**
**~~_AP-160: Write new prompts for GCP_~~**
    """
    expected = """*~_AP-238: New Task for AP Project_~*\n*~_AP-222: Citations_~*\n*~_AP-160: Write new prompts for GCP_~*\n"""
    assert slackify_markdown(markdown) == expected


def test_complex_markdown():
    markdown = """

# Project Overview

Welcome to the **Project X** documentation. This project aims to revolutionize the industry by introducing:

- *Innovative solutions*
- **Cutting-edge technology**
- ~Disruptive strategies~

## Features

1. **User-Friendly Interface**
   - Intuitive design
   - Responsive layouts
2. **Performance**
   - High-speed processing
   - Low latency
3. **Security**
   - Data encryption
   - Regular security audits

## Code Example

Here's a simple Python function:

```python
def greet(name):
    return f"Hello, {name}!"
```

> "Code is like humor. When you have to explain it, it’s bad." – *Cory House*

## Links and Images

For more information, visit our [official website](https://example.com).

![Project Logo](https://example.com/logo.png "Project X Logo")

## Table

| Feature    | Description         |
|------------|---------------------|
| Speed      | Fast performance    |
| Usability  | Easy to use         |
| Security   | Top-notch protection|

## Footnotes

This project is a game-changer[^1].

[^1]: According to industry experts.
    """

    expected_slack_format = """*Project Overview*

Welcome to the *Project X* documentation. This project aims to revolutionize the industry by introducing:

•   _Innovative solutions_
•   *Cutting-edge technology*
•   ~Disruptive strategies~

*Features*

1.  *User-Friendly Interface*
    ◦   Intuitive design
    ◦   Responsive layouts

2.  *Performance*
    ◦   High-speed processing
    ◦   Low latency

3.  *Security*
    ◦   Data encryption
    ◦   Regular security audits

*Code Example*

Here's a simple Python function:

```
def greet(name):
    return f"Hello, {name}!"
```
> "Code is like humor. When you have to explain it, it’s bad." – _Cory House_

*Links and Images*

For more information, visit our <https://example.com|official website>.

<https://example.com/logo.png|Project Logo>

*Table*

| Feature    | Description         |
|------------|---------------------|
| Speed      | Fast performance    |
| Usability  | Easy to use         |
| Security   | Top-notch protection|

*Footnotes*

This project is a game-changer[^1].

[^1]: According to industry experts.
"""

    assert slackify_markdown(markdown) == expected_slack_format


# # Below tests are ported from https://github.com/jsarafajr/slackify-markdown/blob/master/__test__/slackify-markdown.test.js
# # The library originally is inspired from https://github.com/jsarafajr/slackify-markdown


def test_simple_text():
    assert slackify_markdown("""hello world""") == "hello world\n"


def test_escaped_text():
    assert slackify_markdown("*h&ello>world<") == "*h&amp;ello&gt;world&lt;\n"


def test_definitions():
    mrkdown = "hello\n\n[1]: http://atlassian.com\n\nworld\n\n[2]: http://atlassian.com"
    slack = "hello\n\nworld\n"
    assert slackify_markdown(mrkdown) == slack


def test_headings():
    mrkdown = "# heading 1\n## heading 2\n### heading 3"
    slack = "*heading 1*\n\n*heading 2*\n\n*heading 3*\n"
    assert slackify_markdown(mrkdown) == slack


def test_heading_with_bold():
    assert slackify_markdown("### **Step 1**: Description here") == "*Step 1: Description here*\n"
    assert slackify_markdown("### **Step 1**") == "*Step 1*\n"
    assert slackify_markdown("# **Test**: text") == "*Test: text*\n"
    assert slackify_markdown("### Normal and **bold**") == "*Normal and bold*\n"


def test_heading_with_italic():
    assert slackify_markdown("### *emphasized*") == "*_emphasized_*\n"
    assert slackify_markdown("### ***bold italic***") == "*_bold italic_*\n"


def test_bold():
    mrkdown = "**bold text**"
    slack = "*bold text*\n"
    assert slackify_markdown(mrkdown) == slack


def test_bold_character_in_word():
    assert slackify_markdown("he**l**lo") == "he*l*lo\n"


def test_italic():
    mrkdown = "*italic text*"
    slack = "_italic text_\n"
    assert slackify_markdown(mrkdown) == slack


def test_bold_italic():
    mrkdown = "***bold+italic***"
    slack = "_*bold+italic*_\n"
    assert slackify_markdown(mrkdown) == slack


def test_strike():
    mrkdown = "~~strike text~~"
    slack = "~strike text~\n"
    assert slackify_markdown(mrkdown) == slack


def test_unordered_list():
    mrkdown = "* list\n* list\n* list"
    slack = "•   list\n•   list\n•   list\n"
    assert slackify_markdown(mrkdown) == slack


def test_ordered_list():
    mrkdown = "1. list\n2. list\n3. list"
    slack = "1.  list\n2.  list\n3.  list\n"
    assert slackify_markdown(mrkdown) == slack


def test_link_with_alt():
    mrkdown = "[test](http://atlassian.com)"
    slack = "<http://atlassian.com|test>\n"
    assert slackify_markdown(mrkdown) == slack


def test_link_with_angle_bracket_syntax():
    mrkdown = "<http://atlassian.com>"
    slack = "<http://atlassian.com|http://atlassian.com>\n"
    assert slackify_markdown(mrkdown) == slack


def test_link_with_no_alt_nor_title():
    mrkdown = "[](http://atlassian.com)"
    slack = "<http://atlassian.com>\n"
    assert slackify_markdown(mrkdown) == slack


def test_link_with_path_only():
    mrkdown = "[test](/atlassian)"
    slack = "</atlassian|test>\n"
    assert slackify_markdown(mrkdown) == slack


def test_link_in_reference_style_with_alt():

    mrkdown = "[Atlassian]\n\n[atlassian]: http://atlassian.com"
    slack = "<http://atlassian.com|Atlassian>\n"
    assert slackify_markdown(mrkdown) == slack


def test_link_in_reference_style_with_custom_label():
    mrkdown = "[][test]\n\n[test]: http://atlassian.com"
    slack = "<http://atlassian.com>\n"
    assert slackify_markdown(mrkdown) == slack


def test_link_in_reference_style_with_alt_and_custom_label():
    mrkdown = "[Atlassian][test]\n\n[test]: http://atlassian.com"
    slack = "<http://atlassian.com|Atlassian>\n"
    assert slackify_markdown(mrkdown) == slack


def test_link_in_reference_style_with_alt_and_title():
    mrkdown = '[Atlassian]\n\n[atlassian]: http://atlassian.com "Title"'
    slack = "<http://atlassian.com|Atlassian>\n"
    assert slackify_markdown(mrkdown) == slack


def test_link_is_already_encoded():
    mrkdown = "[Atlassian](https://www.atlassian.com?redirect=https%3A%2F%2Fwww.asana.com): /atlassian"
    slack = "<https://www.atlassian.com?redirect=https%3A%2F%2Fwww.asana.com|Atlassian>: /atlassian\n"
    assert slackify_markdown(mrkdown) == slack


def test_link_in_reference_style_with_path_only():
    mrkdown = "[Atlassian][test]\n\n[test]: /atlassian"
    slack = "</atlassian|Atlassian>\n"
    assert slackify_markdown(mrkdown) == slack


def test_image_with_title():
    mrkdown = '![](https://bitbucket.org/repo/123/images/logo.png "test")'
    slack = "<https://bitbucket.org/repo/123/images/logo.png|test>\n"
    assert slackify_markdown(mrkdown) == slack


def test_image_with_alt():
    mrkdown = "![logo.png](https://bitbucket.org/repo/123/images/logo.png)"
    slack = "<https://bitbucket.org/repo/123/images/logo.png|logo.png>\n"
    assert slackify_markdown(mrkdown) == slack


def test_image_with_alt_and_title():
    mrkdown = "![logo.png](https://bitbucket.org/repo/123/images/logo.png 'test')"
    slack = "<https://bitbucket.org/repo/123/images/logo.png|logo.png>\n"
    assert slackify_markdown(mrkdown) == slack


def test_image_with_no_alt_nor_title():
    mrkdown = "![](https://bitbucket.org/repo/123/images/logo.png)"
    slack = "<https://bitbucket.org/repo/123/images/logo.png>\n"
    assert slackify_markdown(mrkdown) == slack


def test_image_with_invalid_url():
    mrkdown = "![logo.png](/relative-path-logo.png 'test')"
    slack = "logo.png\n"
    assert slackify_markdown(mrkdown) == slack


def test_image_in_reference_style_with_alt():
    mrkdown = (
        "![Atlassian]\n\n[atlassian]: https://bitbucket.org/repo/123/images/logo.png"
    )
    slack = "<https://bitbucket.org/repo/123/images/logo.png|Atlassian>\n"
    assert slackify_markdown(mrkdown) == slack


def test_image_in_reference_style_with_custom_label():
    mrkdown = "![][test]\n\n[test]: https://bitbucket.org/repo/123/images/logo.png"
    slack = "<https://bitbucket.org/repo/123/images/logo.png>\n"
    assert slackify_markdown(mrkdown) == slack


def test_image_in_reference_style_with_alt_and_custom_label():
    mrkdown = (
        "![Atlassian][test]\n\n[test]: https://bitbucket.org/repo/123/images/logo.png"
    )
    slack = "<https://bitbucket.org/repo/123/images/logo.png|Atlassian>\n"
    assert slackify_markdown(mrkdown) == slack


def test_image_in_reference_style_with_title():
    mrkdown = (
        '![][test]\n\n[test]: https://bitbucket.org/repo/123/images/logo.png "Title"'
    )
    slack = "<https://bitbucket.org/repo/123/images/logo.png|Title>\n"
    assert slackify_markdown(mrkdown) == slack


def test_image_in_reference_style_with_alt_and_title():
    mrkdown = '![Atlassian]\n\n[atlassian]: https://bitbucket.org/repo/123/images/logo.png "Title"'
    slack = "<https://bitbucket.org/repo/123/images/logo.png|Atlassian>\n"
    assert slackify_markdown(mrkdown) == slack


def test_image_in_reference_style_with_invalid_definition():
    mrkdown = "![Atlassian][test]\n\n[test]: /relative-path-logo.png"
    slack = "Atlassian\n"
    assert slackify_markdown(mrkdown) == slack


def test_inline_code():
    mrkdown = "hello `world`"
    slack = "hello `world`\n"
    assert slackify_markdown(mrkdown) == slack


def test_code_block():
    mrkdown = "```\ncode block\n```"
    slack = "```\ncode block\n```\n"
    assert slackify_markdown(mrkdown) == slack


def test_code_block_with_newlines():
    mrkdown = "```\ncode\n\n\nblock\n```"
    slack = "```\ncode\n\n\nblock\n```\n"
    assert slackify_markdown(mrkdown) == slack


def test_code_block_with_language():
    mrkdown = "```javascript\ncode block\n```"
    slack = "```\ncode block\n```\n"
    assert slackify_markdown(mrkdown) == slack


def test_code_block_with_deprecated_language_declaration():
    mrkdown = "```\n#!javascript\ncode block\n```"
    slack = "```\ncode block\n```\n"
    assert slackify_markdown(mrkdown) == slack


def test_user_mention():
    mrkdown = "<@UPXGB22A2>"
    slack = "<@UPXGB22A2>\n"
    assert slackify_markdown(mrkdown) == slack


# Todo: Add title support
# def test_link_in_reference_style_with_title():
#     mrkdown = '[][test]\n\n[test]: http://atlassian.com "Title"'
#     slack = '<http://atlassian.com|Title>\n'
#     assert slackify_markdown(mrkdown) == slack

# Todo: Add title support
# def test_link_with_title():
#     mrkdown = '[](http://atlassian.com "Atlassian")'
#     slack = '<http://atlassian.com|Atlassian>\n'
#     assert slackify_markdown(mrkdown) == slack


# ---------------------------------------------------------------------------
# Complex / edge-case tests. These exercise the structural-newline cap, code
# block content preservation, deep + mixed list nesting, blockquotes, and the
# STX sentinel scrub. See architecture.md for the rationale behind these.
# ---------------------------------------------------------------------------


def test_deeply_nested_bullet_list_four_levels():
    """Beyond the 3 distinct bullet glyphs, deeper levels reuse the deepest
    glyph but keep adding indent. Trailing block ends with exactly one blank
    line (cap fires on the cascading list_closes)."""
    markdown = (
        "- L1\n"
        "  - L2\n"
        "    - L3\n"
        "      - L4 falls back to deepest bullet\n"
        "        - L5 also falls back\n"
        "\n"
        "After the list."
    )
    expected = (
        "•   L1\n"
        "    ◦   L2\n"
        "        ▪   L3\n"
        "            ▪   L4 falls back to deepest bullet\n"
        "                ▪   L5 also falls back\n"
        "\n"
        "After the list.\n"
    )
    assert slackify_markdown(markdown) == expected


def test_mixed_ordered_unordered_three_levels():
    """Ordered -> unordered -> ordered -> unordered. Each item_open uses the
    right glyph; ordered numbering restarts on the inner level."""
    markdown = (
        "1. Outer ordered\n"
        "   - Unordered child\n"
        "     1. Re-ordered grandchild\n"
        "        - Final bullet\n"
        "2. Second outer\n"
        "\n"
        "After."
    )
    expected = (
        "1.  Outer ordered\n"
        "    ◦   Unordered child\n"
        "        1.  Re-ordered grandchild\n"
        "            ▪   Final bullet\n"
        "\n"
        "2.  Second outer\n"
        "\n"
        "After.\n"
    )
    assert slackify_markdown(markdown) == expected


def test_code_block_preserves_specials_and_blank_lines():
    """Asterisks, underscores, tildes, HTML entities, and multi-blank-line
    spacing all survive inside a fenced code block. The newline cap MUST NOT
    touch code-block content."""
    markdown = (
        "Intro.\n\n"
        "```\n"
        "x = '*not bold*'\n"
        "y = '_not italic_'\n"
        "z = '~not strike~'\n"
        "html = '<div class=\"x\">&amp;</div>'\n"
        "\n"
        "\n"
        "\n"
        "blank_lines_preserved = True\n"
        "```\n\n"
        "Outro."
    )
    expected = (
        "Intro.\n\n"
        "```\n"
        "x = '*not bold*'\n"
        "y = '_not italic_'\n"
        "z = '~not strike~'\n"
        "html = '<div class=\"x\">&amp;</div>'\n"
        "\n\n\n"
        "blank_lines_preserved = True\n"
        "```\n"
        "Outro.\n"
    )
    assert slackify_markdown(markdown) == expected


def test_loose_list_paragraph_per_item():
    """A list with blank lines between items becomes "loose" — each item's
    paragraph_close emits a blank-line separator. The continuation paragraph
    inside the first item is rendered as its own block."""
    markdown = (
        "- First item paragraph one.\n\n"
        "  First item paragraph two.\n\n"
        "- Second item.\n\n"
        "After list."
    )
    expected = (
        "•   First item paragraph one.\n\n"
        "First item paragraph two.\n\n"
        "•   Second item.\n\n"
        "After list.\n"
    )
    assert slackify_markdown(markdown) == expected


def test_blockquote_with_inner_list_and_trailing_paragraph():
    """Blockquote containing a paragraph, a list, and a trailing paragraph.
    The blockquote prefix "> " is emitted only on the first inner paragraph
    (current behavior); inner lists and trailing paragraphs flow as plain
    blocks. Cap keeps everything to single blank-line separators."""
    markdown = (
        "> Intro quoted.\n>\n"
        "> - first bullet inside quote\n"
        "> - second bullet\n>\n"
        "> Trailing quoted paragraph.\n\n"
        "After quote."
    )
    expected = (
        "> Intro quoted.\n\n"
        "•   first bullet inside quote\n"
        "•   second bullet\n\n"
        "Trailing quoted paragraph.\n\n"
        "After quote.\n"
    )
    assert slackify_markdown(markdown) == expected


def test_all_heading_levels_followed_by_body():
    """All six heading levels collapse to Slack's single bold style (*x*),
    each separated by one blank line, followed by a body paragraph."""
    markdown = (
        "# H1\n"
        "## H2\n"
        "### H3\n"
        "#### H4\n"
        "##### H5\n"
        "###### H6\n\n"
        "Body paragraph."
    )
    expected = (
        "*H1*\n\n"
        "*H2*\n\n"
        "*H3*\n\n"
        "*H4*\n\n"
        "*H5*\n\n"
        "*H6*\n\n"
        "Body paragraph.\n"
    )
    assert slackify_markdown(markdown) == expected


def test_multiple_blank_lines_collapse_outside_code_only():
    """Many blank lines between paragraphs collapse to ONE blank line.
    Same many-blank-lines INSIDE a code block are preserved verbatim."""
    markdown = (
        "Para1.\n\n\n\n\n"
        "Para2.\n\n"
        "```\nline1\n\n\n\n\nline2\n```\n\n\n\n"
        "Para3."
    )
    expected = (
        "Para1.\n\n"
        "Para2.\n\n"
        "```\nline1\n\n\n\n\nline2\n```\n"
        "Para3.\n"
    )
    assert slackify_markdown(markdown) == expected


def test_link_with_nested_formatting_and_special_url():
    """Bold/italic/strike inside the link text are preserved, and URL query
    params with & are not double-escaped. Bare <url> autolink gets the same
    <url|url> shape."""
    markdown = (
        "See [**bold _italic ~strike~_** text](https://example.com/path?q=a&b=c) here.\n\n"
        "Plain <https://x.com> autolink."
    )
    expected = (
        "See <https://example.com/path?q=a&b=c|*bold _italic ~strike~_* text> here.\n\n"
        "Plain <https://x.com|https://x.com> autolink.\n"
    )
    assert slackify_markdown(markdown) == expected


def test_inline_code_and_slack_mentions_preserved():
    """Slack mention syntax <@U...>, <!channel>, <#C...|name> must survive
    escape_specials unchanged. Inline code with `<`, `>`, `&` stays literal."""
    markdown = (
        "Hi <@U12345>, try `if a < b && c > d: pass` then ping <!channel>.\n\n"
        "Channel: <#C99999|general>."
    )
    expected = (
        "Hi <@U12345>, try `if a < b && c > d: pass` then ping <!channel>.\n\n"
        "Channel: <#C99999|general>.\n"
    )
    assert slackify_markdown(markdown) == expected


def test_user_input_with_sentinel_chars_does_not_corrupt():
    """If user input contains literal STX (the internal newline sentinel),
    slackify() scrubs it before parsing so it cannot be misread as a
    structural break. ETX is unrelated and passes through to output."""
    stx = chr(0x02)
    etx = chr(0x03)
    markdown = "Hello" + stx + "world and " + etx + " too."
    out = slackify_markdown(markdown)
    # STX was stripped from input; "Hello" and "world" sit adjacent.
    assert stx not in out
    assert "Helloworld" in out
    # ETX is not our sentinel — it survives.
    assert etx in out


def test_full_document_with_all_patterns():
    """Single integration test covering: all six heading levels, bold +
    italic + strike + inline code + links + autolinks, ordered list,
    nested bullets up to depth 3, mixed bold parent items with sub-lists,
    fenced code blocks (plain and language-tagged) sitting between
    paragraphs and after lists, a verbatim Markdown table (Slack does not
    render tables, so it passes through), a blockquote containing an
    inline list and a trailing paragraph, Slack mentions of all flavors,
    URLs with query strings and ampersands, inline code containing
    HTML-special chars, and a tail with many blank lines collapsing to
    one. If anything in the renderer regresses, this test will catch it."""
    markdown = (
        "# Project Documentation\n"
        "\n"
        "A quick **overview** with _emphasis_, ~~deprecated~~, and `inline_code()`. "
        "Visit our [home](https://example.com/?q=a&b=c) or autolink "
        "<https://example.com>.\n"
        "\n"
        "## Features\n"
        "\n"
        "The system supports the following capabilities:\n"
        "\n"
        "1. **Authentication** — multiple providers\n"
        "   - [OAuth2](https://example.com/oauth)\n"
        "   - [SAML](https://example.com/saml)\n"
        "   - Local password fallback\n"
        "2. **Storage**\n"
        "   - Disk\n"
        "   - S3\n"
        "     - Versioning\n"
        "     - Lifecycle rules\n"
        "   - GCS\n"
        "3. **Reliability**\n"
        "\n"
        "## Quick start\n"
        "\n"
        "Install the package:\n"
        "\n"
        "```\n"
        "pip install slackify-markdown\n"
        "```\n"
        "\n"
        "Then use it in your code:\n"
        "\n"
        "```python\n"
        "from slackify_markdown import slackify_markdown\n"
        "\n"
        'result = slackify_markdown("# Hello\\n\\n- item *one*\\n- item _two_")\n'
        "print(result)\n"
        "```\n"
        "\n"
        "The code above will produce mrkdwn ready to post to Slack.\n"
        "\n"
        "## API surface\n"
        "\n"
        "| Function | Description |\n"
        "|----------|-------------|\n"
        "| slackify_markdown(text) | Convert Markdown to mrkdwn |\n"
        "\n"
        "(Tables are passed through as raw text — Slack does not render Markdown tables.)\n"
        "\n"
        "## Things to watch out for\n"
        "\n"
        "> **Important:** Slack mentions like <@U12345>, <#C99999|general>, "
        "and <!channel> must round-trip unchanged.\n"
        ">\n"
        "> - bullet inside a quoted callout\n"
        "> - second bullet\n"
        ">\n"
        "> Trailing quoted paragraph.\n"
        "\n"
        "### Example with everything nested\n"
        "\n"
        "- **Outer item with bold**\n"
        "  - Sub item with a [link](https://example.com)\n"
        "  - Sub item with `inline code`\n"
        "- **Second outer**\n"
        "\n"
        "After the deeply mixed list comes a code-heavy paragraph: "
        '`if x < 0 && y > 0: raise ValueError("&amp;negative")`.\n'
        "\n"
        "#### Conclusion\n"
        "\n"
        "That's it — multiple blank lines below should collapse to one:\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "End."
    )
    expected = (
        "*Project Documentation*\n\n"
        "A quick *overview* with _emphasis_, ~deprecated~, and `inline_code()`. "
        "Visit our <https://example.com/?q=a&b=c|home> or autolink "
        "<https://example.com|https://example.com>.\n\n"
        "*Features*\n\n"
        "The system supports the following capabilities:\n\n"
        "1.  *Authentication* — multiple providers\n"
        "    ◦   <https://example.com/oauth|OAuth2>\n"
        "    ◦   <https://example.com/saml|SAML>\n"
        "    ◦   Local password fallback\n\n"
        "2.  *Storage*\n"
        "    ◦   Disk\n"
        "    ◦   S3\n"
        "        ▪   Versioning\n"
        "        ▪   Lifecycle rules\n\n"
        "    ◦   GCS\n\n"
        "3.  *Reliability*\n\n"
        "*Quick start*\n\n"
        "Install the package:\n\n"
        "```\npip install slackify-markdown\n```\n"
        "Then use it in your code:\n\n"
        "```\nfrom slackify_markdown import slackify_markdown\n\n"
        'result = slackify_markdown("# Hello\\n\\n- item *one*\\n- item _two_")\n'
        "print(result)\n"
        "```\n"
        "The code above will produce mrkdwn ready to post to Slack.\n\n"
        "*API surface*\n\n"
        "| Function | Description |\n"
        "|----------|-------------|\n"
        "| slackify_markdown(text) | Convert Markdown to mrkdwn |\n\n"
        "(Tables are passed through as raw text — Slack does not render Markdown tables.)\n\n"
        "*Things to watch out for*\n\n"
        "> *Important:* Slack mentions like <@U12345>, <#C99999|general>, "
        "and <!channel> must round-trip unchanged.\n\n"
        "•   bullet inside a quoted callout\n"
        "•   second bullet\n\n"
        "Trailing quoted paragraph.\n\n"
        "*Example with everything nested*\n\n"
        "•   *Outer item with bold*\n"
        "    ◦   Sub item with a <https://example.com|link>\n"
        "    ◦   Sub item with `inline code`\n\n"
        "•   *Second outer*\n\n"
        "After the deeply mixed list comes a code-heavy paragraph: "
        '`if x < 0 && y > 0: raise ValueError("&amp;negative")`.\n\n'
        "*Conclusion*\n\n"
        "That's it — multiple blank lines below should collapse to one:\n\n"
        "End.\n"
    )
    assert slackify_markdown(markdown) == expected
