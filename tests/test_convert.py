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
    expected = "•   *Bold* and _Italic_ with ~strike~.\n•   *Bold* and _Italic_ with ~strike~.\n"
    assert slackify_markdown(markdown) == expected


def test_bold_italics_strike_ordered_list():
    markdown = "1. **Bold** and _Italic_ with ~~strike~~.\n\n2. **Bold** and _Italic_ with ~~strike~~.\n\n"
    expected = "1.  *Bold* and _Italic_ with ~strike~.\n2.  *Bold* and _Italic_ with ~strike~.\n"
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
•   Intuitive design
•   Responsive layouts
2.  *Performance*
•   High-speed processing
•   Low latency
3.  *Security*
•   Data encryption
•   Regular security audits
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
    slack = "hello\nworld\n"
    assert slackify_markdown(mrkdown) == slack


def test_headings():
    mrkdown = "# heading 1\n## heading 2\n### heading 3"
    slack = "*heading 1*\n\n*heading 2*\n\n*heading 3*\n\n"
    assert slackify_markdown(mrkdown) == slack


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
