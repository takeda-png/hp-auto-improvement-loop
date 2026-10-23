"""README.md から公開用の index.html（白背景・GitHub Pages）を作る。
usage: python build_page.py
README を直したらこれを流して commit / push する。
"""
import html
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
md = (ROOT / "README.md").read_text(encoding="utf-8")

# mermaid ブロックは GitHub の描画 API に渡さず、ページ側で mermaid.js に描かせる
m = re.search(r"```mermaid\n(.*?)```", md, re.S)
mermaid_src = m.group(1) if m else ""
TOKEN = "MERMAIDPLACEHOLDER0001"
md_for_api = md.replace(m.group(0), TOKEN) if m else md

body = subprocess.run(
    ["gh", "api", "-X", "POST", "markdown", "--input", "-"],
    input=json.dumps({"mode": "gfm", "text": md_for_api}).encode("utf-8"),
    capture_output=True, check=True,
).stdout.decode("utf-8")
body = body.replace(f"<p>{TOKEN}</p>", f'<pre class="mermaid">{html.escape(mermaid_src)}</pre>')
assert TOKEN not in body

page = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HP自動改善ループ</title>
<meta name="description" content="アクセス解析×SFA×Clarityを毎月つなぎ、3か月ごとにHPを直す仕組みと、自社サイトで回した2026年10月の結果。">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css@5.5.1/github-markdown-light.css">
<style>
  :root {{ color-scheme: light; }}
  html, body {{ background: #ffffff; margin: 0; }}
  .markdown-body {{ box-sizing: border-box; max-width: 980px; margin: 0 auto; padding: 40px 16px 64px; }}
  .markdown-body table {{ display: block; overflow-x: auto; }}
  .markdown-body img {{ background: #fff; }}
  pre.mermaid {{ background: #ffffff; border: 1px solid #e5e7eb; text-align: center; overflow-x: auto; }}
</style>
</head>
<body>
<article class="markdown-body">
{body}
</article>
<script type="module">
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.esm.min.mjs";
  mermaid.initialize({{ startOnLoad: true }});
</script>
</body>
</html>
"""
(ROOT / "index.html").write_bytes(page.encode("utf-8"))
print("index.html", len(page), "chars")
