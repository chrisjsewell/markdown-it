# if __name__ == "__main__":

from markdown_it import MarkdownIt
from markdown_it.doc_renderer import DocRenderer
md = MarkdownIt()
tokens = md.parse("""\
# title
a
- b *c* **g**
    - h
d
> +++
---
` a `
```a dfg
mj
```
## a


""")

# print(get_nested(tokens))

doc = DocRenderer()
doc.run_render(tokens)
print(doc.document.pformat())
