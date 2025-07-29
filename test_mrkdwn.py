from markdown_to_mrkdwn import SlackMarkdownConverter

markdown = """```
ok
```
`ok`
```ok```
*ok*"""

converter = SlackMarkdownConverter()
print("Input:")
print(markdown)
print("\nOutput:")
print(converter.convert(markdown)) 