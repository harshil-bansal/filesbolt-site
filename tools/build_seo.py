"""Rebuilds the search/AI files from updates/releases.json and the home page.

Run from the site folder:  python3 tools/build_seo.py [--add <version> <notes-file>]
Writes: updates/index.html, updates/feed.xml, sitemap.xml, ai/summary.json, ai/faq.json,
ai/service.json, .well-known/ai.txt, and the dates in index.html.
The publish-download workflow runs this with --add after each release.
"""
import datetime as dt
import html
import json
import re
import sys
from email.utils import format_datetime

SITE = "https://filesbolt.com"
LAUNCHED = "2026-11-11"
REL = "updates/releases.json"


def esc(s):
    return html.escape(s, quote=True)


def load():
    return json.load(open(REL, encoding="utf-8"))


def add_release(ver, notes):
    rows = [r for r in load() if r["version"] != ver]
    rows.insert(0, {"version": ver, "date": dt.date.today().isoformat(), "notes": notes.strip()})
    json.dump(rows, open(REL, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def nice(d):
    d = dt.date.fromisoformat(d)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def faq_items(page):
    out = []
    for q, a in re.findall(r"<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>", page, re.S):
        t = lambda x: html.unescape(re.sub(r"<[^>]+>", "", x)).strip()
        out.append({"question": t(q), "answer": t(a)})
    return out


def page_shell(src, title, desc, canonical, body):
    """Reuse privacy.html's head, header and footer so new pages match the site."""
    head, rest = src.split("<main", 1)
    foot = src[src.index("<footer"):]
    head = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", head)
    head = re.sub(r'<meta name="description"[^>]*>', f'<meta name="description" content="{esc(desc)}">', head)
    head = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{canonical}">', head)
    head = head.replace('href="img/', 'href="/img/').replace('src="img/', 'src="/img/').replace('href="style.css"', 'href="/style.css"')
    head = head.replace("</head>", '<link rel="alternate" type="application/rss+xml" title="FilesBolt updates" href="/updates/feed.xml">\n</head>')
    foot = foot.replace('href="terms.html"', 'href="/terms.html"').replace('href="refunds.html"', 'href="/refunds.html"') \
        .replace('href="privacy.html"', 'href="/privacy.html"').replace('src="img/', 'src="/img/')
    return head + body + "\n" + foot


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "--add":
        add_release(sys.argv[2], open(sys.argv[3], encoding="utf-8").read())
    rel = load()
    latest = rel[0]
    mod = latest["date"]
    index = open("index.html", encoding="utf-8").read()

    # --- What's new page + RSS
    items = []
    for r in rel:
        lis = "".join(f"<li>{esc(x.strip())}</li>" for x in r["notes"].split("\n") if x.strip())
        items.append(f'    <article class="rel"><h2>FilesBolt {esc(r["version"])}</h2>'
                     f'<p class="updated"><time datetime="{r["date"]}">{nice(r["date"])}</time></p><ul>{lis}</ul></article>')
    body = ('<main class="doc">\n  <div class="wrap narrow">\n    <h1>What\'s new in FilesBolt</h1>\n'
            '    <p>FilesBolt updates itself: when a new version is out, the app offers a one-click update. '
            'You can also <a href="/#download">download the latest version</a>. '
            '<a href="/updates/feed.xml">RSS feed</a></p>\n' + "\n".join(items) + "\n  </div>\n</main>")
    src = open("privacy.html", encoding="utf-8").read()
    open("updates/index.html", "w", encoding="utf-8").write(page_shell(
        src, "What's new | FilesBolt", "New features and fixes in each FilesBolt update for Windows.",
        f"{SITE}/updates/", body))

    def rfc(d):
        return format_datetime(dt.datetime.fromisoformat(d + "T12:00:00+00:00"))
    rss = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0"><channel>',
           "<title>FilesBolt updates</title>", f"<link>{SITE}/updates/</link>",
           "<description>New features and fixes in each FilesBolt update.</description>",
           "<language>en</language>", f"<lastBuildDate>{rfc(mod)}</lastBuildDate>"]
    for r in rel:
        rss.append(f"<item><title>FilesBolt {esc(r['version'])}</title><link>{SITE}/updates/</link>"
                   f"<guid isPermaLink=\"false\">filesbolt-{esc(r['version'])}</guid><pubDate>{rfc(r['date'])}</pubDate>"
                   f"<description>{esc(r['notes'])}</description></item>")
    rss.append("</channel></rss>")
    open("updates/feed.xml", "w", encoding="utf-8").write("\n".join(rss) + "\n")

    # --- Home page dates (schema + visible)
    index = re.sub(r'"dateModified": "[^"]*"', f'"dateModified": "{mod}"', index)
    index = re.sub(r'"softwareVersion": "[^"]*"', f'"softwareVersion": "{latest["version"]}"', index)
    index = re.sub(r'<dd data-date>.*?</dd>', f'<dd data-date><time datetime="{mod}">{nice(mod)}</time></dd>', index)
    open("index.html", "w", encoding="utf-8").write(index)

    # --- Sitemap
    pages = [("", mod), ("updates/", mod), ("about/", None), ("pricing/", None), ("contact/", None), ("privacy.html", None), ("terms.html", None), ("refunds.html", None)]
    try:
        from build_tool_pages import PAGES as TOOL_PAGES, HI as HI_PAGES, ES as ES_PAGES
        pages += [(f"{k}/", None) for k in TOOL_PAGES] + [(f"hi/{k}/", None) for k in HI_PAGES] + [(f"es/{k}/", None) for k in ES_PAGES]
    except Exception:
        pass
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p, d in pages:
        sm.append(f"  <url><loc>{SITE}/{p}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>")
    sm.append("</urlset>")
    open("sitemap.xml", "w", encoding="utf-8").write("\n".join(sm) + "\n")

    # --- AI discovery files
    desc = ("FilesBolt is an offline Windows app (Windows 10 and 11) that merges, compresses and converts PDFs, "
            "photos and Excel files on your own PC, from the right-click menu or its own window. Files are never uploaded.")
    summary = {"name": "FilesBolt", "url": SITE + "/", "description": desc, "category": "Desktop file utility (PDF, images, Excel)",
               "platform": ["Windows 10", "Windows 11"], "price": "Free during launch", "latestVersion": latest["version"],
               "updated": mod, "download": SITE + "/#download", "contact": SITE + "/contact/",
               "languages": ["English", "Spanish", "French", "German", "Hindi"]}
    service = {"name": "FilesBolt", "url": SITE + "/", "type": "SoftwareApplication", "offline": True, "uploadsFiles": False,
               "capabilities": {
                   "Organize": ["Merge PDFs, photos and Office files into one PDF", "Split pages", "Reorder, rotate or remove pages"],
                   "Convert": ["Photos (JPG, PNG, HEIC, TIFF) to PDF", "PDF to JPG", "PDF to Word", "PDF tables to Excel",
                               "Word and PowerPoint to PDF (with Microsoft Office installed)"],
                   "Shrink": ["Compress PDFs and photos", "Resize photos for email", "Repair PDFs"],
                   "Edit": ["Edit and sign PDFs", "Watermark", "Page numbers"],
                   "Excel": ["Combine Excel files", "Split sheets", "CSV to Excel and back"],
                   "Protect and pack": ["Add or remove a PDF password", "Make or extract ZIP files"]},
               "updated": mod}
    json.dump(summary, open("ai/summary.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump({"updated": mod, "faq": faq_items(index)}, open("ai/faq.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(service, open("ai/service.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    open(".well-known/ai.txt", "w", encoding="utf-8").write(
        "# FilesBolt - AI usage\n# AI assistants and search engines may read, index and cite this site.\n"
        "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /reset/\nDisallow: /unsubscribe/\n\n"
        f"Summary: {SITE}/ai/summary.json\nFAQ: {SITE}/ai/faq.json\nService: {SITE}/ai/service.json\n"
        f"LLMs: {SITE}/llms.txt\nSitemap: {SITE}/sitemap.xml\n")
    print("built; latest", latest["version"], mod)


if __name__ == "__main__":
    main()
