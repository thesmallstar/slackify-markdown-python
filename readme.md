# Slackify Markdown

A Python library for converting Markdown to slack specific markdown. This is inspired from existing npm package [slackify-markdown](https://www.npmjs.com/package/slackify-markdown)

## Overview

This library converts regular Markdown to Slack-specific markdown, making it easy to use and display correctly in Slack messages.

## Installation

```bash
pip install slackify-markdown
```

## Usage

```python
from slackify_markdown import slackify

# Convert markdown to Slack mrkdwn
from slackify_markdown import slackify_markdown

markdown = """
# Title

This is **bold text** and this is *italic text*.

## Subtitle
1. **Item 1**
2. *Item 2*

## Another Subtitle
* **Element 1** - *Description 1*
* **Element 2** - *Description 2*

[Link](https://example.com)

"""

slack_output = slackify_markdown(markdown)
"""
*Title*

This is *bold text* and this is _italic text_.

*Subtitle*
1.  *Item 1*
2.  _Item 2_

*Another Subtitle*
•   *Element 1* - _Description 1_
•   *Element 2* - _Description 2_

<https://example.com|Link>
"""
```

## Features

- Converts headers to Slack-compatible bold text
- Preserves bold and italic formatting
- Handles code blocks and inline code
- Converts links to Slack's expected format
- Processes lists (ordered and unordered)
- Handles blockquotes

## Example Conversions

| Markdown | Slack mrkdwn |
|----------|--------------|
| `# Heading` | `*Heading*` |
| `**Bold**` | `*Bold*` |
| `*Italic*` | `_Italic_` |
| `` `code` `` | `` `code` `` |
| `[Link](https://example.com)` | `<https://example.com\|Link>` |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

Shoutout to [jsarafaj](https://github.com/jsarafajr), his JS library has inspired the code and tests for this package.