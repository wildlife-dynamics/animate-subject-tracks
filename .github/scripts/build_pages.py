"""Render README.md into a static Pages site, alongside a copy of USER_GUIDE.pdf."""

import pathlib

import markdown

SITE_DIR = pathlib.Path("_site")
TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Animate Subject Tracks — User Guide</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1.5rem; line-height: 1.6; color: #1a1a1a; }}
  h1, h2, h3 {{ line-height: 1.25; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
  th, td {{ border: 1px solid #ddd; padding: 0.5rem 0.75rem; text-align: left; }}
  th {{ background: #f6f6f6; }}
  code {{ background: #f2f2f2; padding: 0.1rem 0.35rem; border-radius: 3px; }}
  blockquote {{ border-left: 4px solid #ddd; margin: 1rem 0; padding: 0.25rem 1rem; color: #555; }}
  .guide-link {{ display: inline-block; margin: 1rem 0; padding: 0.6rem 1.2rem; background: #2563eb; color: #fff; border-radius: 6px; text-decoration: none; }}
  .guide-link:hover {{ background: #1d4ed8; }}
</style>
</head>
<body>
<a class="guide-link" href="USER_GUIDE.pdf">Download the full USER_GUIDE.pdf</a>
{body}
</body>
</html>
"""


def main() -> None:
    SITE_DIR.mkdir(exist_ok=True)
    readme = pathlib.Path("README.md").read_text()
    body = markdown.markdown(readme, extensions=["tables", "fenced_code"])
    (SITE_DIR / "index.html").write_text(TEMPLATE.format(body=body))
    (SITE_DIR / "USER_GUIDE.pdf").write_bytes(pathlib.Path("USER_GUIDE.pdf").read_bytes())


if __name__ == "__main__":
    main()
