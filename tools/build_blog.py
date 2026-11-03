"""Build the blog pages for the portfolio.

  blog-src/*.md  ->  blog/<slug>.html, blog/index.html, and the cards inside index.html (between the BLOGS markers)

Run from the repo root (needs pandoc on PATH):   python tools/build_blog.py
Add a post: create blog-src/NN-your-slug.md with this header, then re-run.
    ---
    title: "..."
    date: 2026-11-03
    tags: [Tag1, Tag2]
    summary: "One sentence."
    ---
"""
import html, math, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT, INDEX = ROOT / "blog-src", ROOT / "blog", ROOT / "index.html"
TITLE = "Kishan K — Blog"
LINKS = [("Portfolio", "../index.html"), ("GitHub", "https://github.com/kishanaik5"),
         ("LinkedIn", "https://linkedin.com/in/kishan-k-823049259"), ("Hugging Face", "https://huggingface.co/kishanaik5")]


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    meta, body = {}, text
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"')
        body = m.group(2)
    tags = [t.strip() for t in meta.get("tags", "").strip("[]").split(",") if t.strip()]
    return meta, tags, body


def md_to_html(md):
    return subprocess.run(["pandoc", "-f", "markdown", "-t", "html5", "--wrap=none", "--no-highlight"], input=md,
                          capture_output=True, text=True, encoding="utf-8", check=True).stdout


CSS = """
:root{--bg:#060d1f;--card:#112240;--fg:#e2e8f0;--muted:#94a3b8;--line:#1e3a5f;--accent:#64ffda;--code:#0c1a33}
body.light{--bg:#dce4ef;--card:#c8d5e3;--fg:#1e2d3d;--muted:#3d5068;--line:#96aec4;--accent:#1a4a8a;--code:#cfdbe8}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.75 'Roboto',sans-serif;transition:background .4s,color .4s}
h1,h2,h3{font-family:'Poppins',sans-serif;line-height:1.25}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:780px;margin:0 auto;padding:0 22px}
header{position:sticky;top:0;z-index:5;backdrop-filter:blur(8px);background:color-mix(in srgb,var(--bg) 82%,transparent);border-bottom:1px solid var(--line)}
header .in{display:flex;justify-content:space-between;align-items:center;height:68px;max-width:960px;margin:0 auto;padding:0 22px}
.brand{font:700 1.35rem 'Poppins',sans-serif;color:var(--accent)}
nav a{margin-left:20px;color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.12em}nav a:hover{color:var(--accent);text-decoration:none}
button.t{background:none;border:1px solid var(--line);color:var(--accent);border-radius:8px;padding:5px 10px;margin-left:18px;cursor:pointer}
.hero{padding:70px 0 20px}.eyebrow{font:500 .95rem monospace;color:var(--accent)}
.hero h1{font-size:clamp(2.1rem,6vw,3.2rem);margin:.2em 0 .3em}.hero p{color:var(--muted);font-size:1.1rem;max-width:620px;margin:0}
.grid{display:grid;gap:22px;margin:34px 0 70px}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:26px 28px;color:inherit;transition:transform .2s,border-color .2s,box-shadow .2s}
.card:hover{transform:translateY(-3px);border-color:var(--accent);box-shadow:0 14px 34px rgba(0,0,0,.28);text-decoration:none}
.card h2{margin:0 0 8px;font-size:1.28rem;color:var(--fg)}.card p{margin:8px 0 14px;color:var(--muted);font-size:.98rem}
.meta{font-size:.84rem;color:var(--muted)}
.tag{display:inline-block;font-size:.78rem;padding:3px 11px;margin:0 8px 6px 0;border-radius:4px;background:rgba(100,255,218,.1);border:1px solid rgba(100,255,218,.22);color:var(--accent)}
body.light .tag{background:rgba(26,74,138,.08);border-color:rgba(26,74,138,.25)}
article{padding:54px 0 24px}article h1{font-size:clamp(1.9rem,5vw,2.6rem);margin:0 0 12px}
article h2{margin:2.1em 0 .5em;font-size:1.45rem;color:var(--accent)}
article table{border-collapse:collapse;width:100%;margin:1.3em 0;font-size:.95rem}
article th,article td{border:1px solid var(--line);padding:9px 13px;text-align:left}article th{background:var(--card)}
article code{background:var(--code);padding:2px 7px;border-radius:5px;font:.88em 'Fira Code',Consolas,monospace}
article pre{background:var(--code);padding:15px;border-radius:8px;overflow:auto}
article blockquote{margin:1.3em 0;padding:.2em 1.1em;border-left:3px solid var(--accent);color:var(--muted)}
.back{display:inline-block;margin:34px 0 10px;font-family:monospace}
footer{border-top:1px solid var(--line);padding:30px 0 50px;color:var(--muted);font-size:.9rem;text-align:center}footer a{margin:0 10px}
@media(max-width:560px){body{font-size:16px}nav a{margin-left:12px}}
"""

JS = """(function(){var k='kk-theme',b=document.body;try{if(localStorage.getItem(k)==='light')b.classList.add('light')}catch(e){}
function sync(){var i=document.querySelector('.t i');if(i)i.className=b.classList.contains('light')?'fas fa-sun':'fas fa-moon'}sync();
document.addEventListener('click',function(e){if(e.target.closest('.t')){b.classList.toggle('light');try{localStorage.setItem(k,b.classList.contains('light')?'light':'dark')}catch(x){}sync()}});})();"""


def page(title, desc, body, p=""):
    foot = "".join(f'<a href="{u}">{n}</a>' for n, u in LINKS)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:type" content="article">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><header><div class="in"><a class="brand" href="../index.html">Kishan K</a><span><nav style="display:inline"><a href="index.html">Blog</a><a href="../index.html">Portfolio</a></nav><button class="t" aria-label="Toggle theme"><i class="fas fa-moon"></i></button></span></div></header>
<div class="wrap">{body}<footer>{foot}<br><br>© Kishan K. Views are my own; no employer code or data is published here.</footer></div><script>{JS}</script></body></html>"""


def tags_html(tags):
    return "".join(f"<span class=tag>{html.escape(t)}</span>" for t in tags)


def main():
    posts = []
    for md in sorted(SRC.glob("*.md")):
        meta, tags, body = parse(md)
        words = len(re.findall(r"\w+", body))
        posts.append(dict(slug=md.stem, title=meta.get("title", md.stem), date=meta.get("date", ""), summary=meta.get("summary", ""),
                          tags=tags, mins=max(1, math.ceil(words / 220)), html=md_to_html(body)))
    posts.sort(key=lambda x: (x["date"], x["slug"]))          # oldest first -> numbered order
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.html"): old.unlink()
    cards = "".join(f'<a class="card" href="{x["slug"]}.html"><h2>{html.escape(x["title"])}</h2><p>{html.escape(x["summary"])}</p>'
                    f'<div class="meta">{tags_html(x["tags"])}<br>{x["date"]} · {x["mins"]} min read</div></a>' for x in posts)
    hero = '<section class="hero"><div class="eyebrow">Blog</div><h1>Engineering notes from production AI.</h1><p>Honest write-ups on fine-tuning, evaluation, computer vision and LLM systems: what I measured, what I got wrong, and what I would do differently.</p></section>'
    (OUT / "index.html").write_text(page(TITLE, "Honest engineering notes on ML, LLMs and computer vision.", hero + f'<div class="grid">{cards}</div>'), encoding="utf-8")
    for x in posts:
        body = (f'<article><h1>{html.escape(x["title"])}</h1><div class="meta">{tags_html(x["tags"])} {x["date"]} · {x["mins"]} min read</div>'
                f'{x["html"]}<a class="back" href="index.html">← All posts</a></article>')
        (OUT / f'{x["slug"]}.html').write_text(page(f'{x["title"]} — Kishan K', x["summary"], body), encoding="utf-8")
    # cards on the portfolio home page, in the site's own card style
    portfolio_cards = "\n".join(
        f'<a href="blog/{x["slug"]}.html" class="project-card rounded-lg shadow-lg p-8 reveal block">'
        f'<div><div class="flex justify-between items-center mb-5"><i class="fas fa-pen-nib text-teal text-3xl"></i>'
        f'<span class="text-xs text-gray-400 font-mono">{x["mins"]} min read</span></div>'
        f'<h3 class="text-xl font-bold mb-3 text-gray-100">{html.escape(x["title"])}</h3>'
        f'<p class="text-gray-400 text-sm leading-relaxed mb-4">{html.escape(x["summary"])}</p></div>'
        f'<div>{"".join(f"<span class=skill-tag>{html.escape(t)}</span>" for t in x["tags"])}</div></a>' for x in posts)
    idx = INDEX.read_text(encoding="utf-8")
    new = re.sub(r"(<!-- BLOGS:START -->).*?(<!-- BLOGS:END -->)", lambda m: f"{m.group(1)}\n{portfolio_cards}\n{m.group(2)}", idx, flags=re.S)
    if new == idx and portfolio_cards not in idx:
        raise SystemExit("BLOGS markers not found in index.html")
    INDEX.write_text(new, encoding="utf-8")
    print(f"built {len(posts)} posts -> {OUT} and updated index.html cards")


if __name__ == "__main__":
    main()
