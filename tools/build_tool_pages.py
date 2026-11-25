"""Make one simple page per popular job (filesbolt.com/merge-pdf/ etc.), using the About page's header and footer.
Run: python tools/build_tool_pages.py   (then build_seo.py adds them to the sitemap)."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = (ROOT / "about" / "index.html").read_text(encoding="utf-8")
HEAD_END = TPL.index("<main")
FOOT_START = TPL.index("</main>") + len("</main>")

PAGES = {
    "merge-pdf": dict(
        title="Merge PDF files offline on Windows",
        h1="Merge PDFs into one file, without uploading them",
        desc="Combine PDFs, photos and Word files into one PDF on your own PC. Right-click, choose Merge, done. Free during launch.",
        intro="Select the files in File Explorer, right-click and choose <b>FilesBolt → Merge into one PDF</b>. "
              "The merged PDF appears next to your files in a second or two. Nothing is uploaded.",
        steps=["Select the PDFs, photos or Word files in File Explorer.", "Right-click and choose FilesBolt → Merge into one PDF.",
               "Find Merged.pdf in the same folder."],
        faq=[("Can I change the order?", "Yes. Open FilesBolt, add the files, drag them into the order you want and click Merge."),
             ("Can I merge photos and Word files too?", "Yes. Photos (JPG, PNG, HEIC and more) and Office files are turned into PDF pages as they're merged."),
             ("Is there a file size or page limit?", "No. Everything runs on your PC, so there's no upload limit.")]),
    "compress-pdf": dict(
        title="Compress PDF offline: smaller PDFs on your PC",
        h1="Make PDFs smaller, without uploading them",
        desc="Shrink PDFs and photos for email on your own PC. FilesBolt only saves a copy when it really is smaller.",
        intro="Right-click a PDF and choose <b>FilesBolt → Compress</b>. You get a smaller copy next to the original, and "
              "FilesBolt tells you when a file is already as small as it can be.",
        steps=["Right-click the PDF (or several) in File Explorer.", "Choose FilesBolt → Compress.",
               "The smaller copy is saved next to the original."],
        faq=[("Will the quality drop?", "Text stays sharp. Pictures inside the PDF are resized to what's needed on the page, and you can pick Balanced or Smallest in the app."),
             ("Why didn't my file get smaller?", "Some PDFs are already compact (mostly text). FilesBolt never gives you a bigger file."),
             ("Are my files uploaded?", "No. Compression happens on your computer.")]),
    "pdf-to-jpg": dict(
        title="PDF to JPG offline: turn PDF pages into pictures",
        h1="Turn PDF pages into JPG pictures on your PC",
        desc="Convert every page of a PDF to a JPG image, offline. Right-click, Convert to JPG.",
        intro="Right-click a PDF and choose <b>FilesBolt → Convert to JPG</b>. Each page becomes a sharp JPG in the same folder.",
        steps=["Right-click the PDF.", "Choose FilesBolt → Convert to JPG.", "One JPG per page appears next to the PDF."],
        faq=[("Can I get PNG instead?", "Yes. Open FilesBolt and choose PNG."),
             ("What about password-protected PDFs?", "FilesBolt asks for the password first.")]),
    "jpg-to-pdf": dict(
        title="JPG to PDF offline: photos (and HEIC) to PDF",
        h1="Turn photos into a PDF, without uploading them",
        desc="Convert JPG, PNG and iPhone HEIC photos to PDF on your PC. One PDF per photo, or all photos in one PDF.",
        intro="Select your photos, right-click and choose <b>FilesBolt → Convert to PDF</b> for one PDF per photo, or "
              "<b>Merge into one PDF</b> to put them all in one file. Phone photos are turned the right way up.",
        steps=["Select the photos in File Explorer.", "Right-click: FilesBolt → Convert to PDF (or Merge into one PDF).",
               "The PDF is saved next to the photos."],
        faq=[("Does it work with iPhone HEIC photos?", "Yes, HEIC and HEIF are supported, along with JPG, PNG, WEBP, TIFF and more."),
             ("Is there a limit on how many photos?", "No. Everything runs on your PC.")]),
    "resize-image": dict(
        title="Resize images for email: under 100 KB to 1 MB",
        h1="Make photos smaller for email, forms and uploads",
        desc="Resize photos on your PC to a size, or under 100 KB, 200 KB, 500 KB or 1 MB, for forms that limit file size.",
        intro="Right-click a photo and choose <b>FilesBolt → Resize for email (under 500 KB)</b>. In the app you can also pick "
              "Small, Medium or Large, or a file size limit such as under 100 KB, which many online forms ask for.",
        steps=["Right-click the photos.", "Choose FilesBolt → Resize for email (under 500 KB).",
               "A smaller copy is saved next to each photo; the original isn't changed."],
        faq=[("Can I resize to under 100 KB for a government form?", "Yes. In the app choose Resize images → Under 100 KB."),
             ("Will my phone photos be sideways?", "No. They're turned the right way up before resizing.")]),
    "sign-pdf": dict(
        title="Sign a PDF offline on Windows",
        h1="Sign and fill PDFs on your PC",
        desc="Add your signature, text, dates, check marks and stamps to a PDF, offline. Your signature is kept on your PC.",
        intro="Right-click a PDF and choose <b>FilesBolt → Edit and sign</b>. Draw or type your signature once, place it, add "
              "text or today's date, and save. A signed copy is saved next to the original.",
        steps=["Right-click the PDF and choose FilesBolt → Edit and sign.", "Add your signature, text, date or check marks.",
               "Click Save: a _signed copy appears next to the original."],
        faq=[("Is my signature uploaded?", "No. It's saved only on your PC so you can reuse it."),
             ("Can I white out or move things on the page?", "Yes: whiteout, and Select lets you move, copy, delete or crop part of a page.")]),
    "split-pdf": dict(
        title="Split PDF pages offline",
        h1="Split a PDF into pages, on your PC",
        desc="Save every page of a PDF as its own file, or pick the pages you need. Offline and private.",
        intro="Right-click a PDF and choose <b>FilesBolt → Split into pages</b> to save every page as its own PDF, or open "
              "FilesBolt to pick just the pages you want.",
        steps=["Right-click the PDF.", "Choose FilesBolt → Split into pages.", "The pages are saved in a new folder next to it."],
        faq=[("Can I pick only some pages?", "Yes. In the app choose Split pages and tick the pages you need."),
             ("Can I reorder or remove pages instead?", "Yes, use Organize pages.")]),
    "protect-pdf": dict(
        title="Password protect a PDF offline",
        h1="Add a password to a PDF, on your PC",
        desc="Lock a PDF with a password before you send it, or remove a password you know. Offline.",
        intro="Right-click a PDF and choose <b>FilesBolt → Protect with a password</b>. The protected copy needs the password to open.",
        steps=["Right-click the PDF.", "Choose FilesBolt → Protect with a password.", "Type the password; a protected copy is saved."],
        faq=[("Can I remove a password?", "Yes, if you know it: use Remove password in the app."),
             ("Is the password sent anywhere?", "No. It never leaves your PC.")]),
}


def page(slug, p):
    url = f"https://filesbolt.com/{slug}/"
    head = TPL[:HEAD_END]
    head = re.sub(r"<title>.*?</title>", f"<title>{html.escape(p['title'])} | FilesBolt</title>", head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(p["desc"])}">', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', head)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "HowTo", "name": p["h1"], "step": [{"@type": "HowToStep", "position": i + 1, "text": s} for i, s in enumerate(p["steps"])]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]},
    ]}
    head = head.replace("</head>", f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n</head>')
    steps = "".join(f"<li>{html.escape(s)}</li>" for s in p["steps"])
    faq = "".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q, a in p["faq"])
    others = " · ".join(f'<a href="/{s}/">{html.escape(PAGES[s]["h1"].split(",")[0])}</a>' for s in PAGES if s != slug)
    body = f"""<main class="doc">
  <div class="wrap narrow">
    <h1>{html.escape(p['h1'])}</h1>
    <p>{p['intro']}</p>
    <h2>How to do it</h2>
    <ol>{steps}</ol>
    <p><a class="btn" href="/#download">Download FilesBolt for Windows</a></p>
    <h2>Why offline?</h2>
    <p>Online PDF websites make you upload your files to their servers. FilesBolt does the same jobs on your own computer, so
    your contracts, IDs and invoices never leave it. It works without internet, with no file size limits and no waiting for uploads.</p>
    <h2>Questions</h2>
    {faq}
    <h2>More things FilesBolt does</h2>
    <p>{others}</p>
  </div>
</main>"""
    return head + body + TPL[FOOT_START:]


if __name__ == "__main__":
    for slug, p in PAGES.items():
        d = ROOT / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page(slug, p), encoding="utf-8")
    print(len(PAGES), "pages")
