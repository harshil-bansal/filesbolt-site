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

PAGES.update({
    "pdf-to-word": dict(
        title="PDF to Word offline on Windows",
        h1="Turn a PDF into an editable Word file, on your PC",
        desc="Convert PDF to Word (.docx) without uploading. Uses Microsoft Word when you have it for the best layout.",
        intro="Right-click a PDF and choose <b>FilesBolt → Convert PDF to Word</b>. With Microsoft Word installed you get its "
              "full-quality conversion; without it, FilesBolt makes a simpler .docx you can still edit.",
        steps=["Right-click the PDF.", "Choose FilesBolt → Convert PDF to Word.", "Open the .docx saved next to the PDF."],
        faq=[("Do I need Microsoft Word?", "No, but with Word 2013 or newer the layout is closer to the original."),
             ("What about scanned PDFs?", "Scans are pictures of text, so the text can't be edited yet.")]),
    "heic-to-jpg": dict(
        title="HEIC to JPG on Windows, offline",
        h1="Convert iPhone HEIC photos to JPG",
        desc="Turn iPhone HEIC photos into JPG on your Windows PC with a right-click. No upload, no app store codec needed.",
        intro="Select the HEIC photos, right-click and choose <b>FilesBolt → Convert to JPG</b>. JPG copies appear next to them, "
              "the right way up.",
        steps=["Select the .heic photos in File Explorer.", "Right-click: FilesBolt → Convert to JPG.", "The JPGs are saved next to the originals."],
        faq=[("Do I need to install a HEIC extension from Microsoft?", "No. FilesBolt reads HEIC by itself."),
             ("Can I make a PDF from HEIC photos?", "Yes: choose Convert to PDF or Merge into one PDF.")]),
    "rotate-pdf": dict(
        title="Rotate PDF pages offline",
        h1="Rotate a PDF or photo, on your PC",
        desc="Turn sideways PDF pages or photos the right way with a right-click. Offline.",
        intro="Right-click a PDF or photo and choose <b>FilesBolt → Rotate right</b>. To turn only some pages, open FilesBolt and "
              "use Organize pages.",
        steps=["Right-click the PDF or photo.", "Choose FilesBolt → Rotate right.", "A rotated copy is saved next to it."],
        faq=[("Can I rotate just one page?", "Yes, with Organize pages in the app.")]),
    "watermark-pdf": dict(
        title="Add a watermark to a PDF offline",
        h1="Add a watermark to a PDF, on your PC",
        desc="Stamp text like CONFIDENTIAL or DRAFT on every page of a PDF. Any text, colour and position. Offline.",
        intro="Open FilesBolt, add the PDF and choose <b>Watermark</b>. Type the text, pick the colour, size and position, and save.",
        steps=["Open FilesBolt and add the PDF.", "Choose Watermark and type your text.", "Save: a watermarked copy appears next to the original."],
        faq=[("Can I add page numbers too?", "Yes, with Page numbers.")]),
    "combine-excel": dict(
        title="Combine Excel files into one, offline",
        h1="Combine Excel and CSV files into one workbook",
        desc="Put several Excel or CSV files into one workbook, each as its own sheet or all rows stacked. On your PC.",
        intro="Select the files, right-click and choose <b>FilesBolt → Combine into one Excel file</b>. In the app you can choose "
              "one sheet per file, or all rows in one sheet.",
        steps=["Select the .xlsx or .csv files.", "Right-click: FilesBolt → Combine into one Excel file.", "Open Combined.xlsx in the same folder."],
        faq=[("Does it keep formatting?", "Values, formulas and basic formatting are kept."),
             ("Can I split a workbook into files?", "Yes: Split sheets saves each sheet as its own file.")]),
    "unlock-pdf": dict(
        title="Remove a PDF password offline",
        h1="Remove the password from a PDF you can open",
        desc="Save a copy of a password-protected PDF without the password, when you know it. On your PC.",
        intro="Open FilesBolt, add the PDF and choose <b>Remove password</b>. Type the current password and an unlocked copy is saved.",
        steps=["Open FilesBolt and add the PDF.", "Choose Remove password and type the current password.", "An unlocked copy is saved next to it."],
        faq=[("Can it unlock a PDF if I don't know the password?", "No. You need the correct password.")]),
})


def page(slug, p):
    url = f"https://filesbolt.com/{slug}/"
    head = TPL[:HEAD_END]
    head = re.sub(r"<title>.*?</title>", f"<title>{html.escape(p['title'])} | FilesBolt</title>", head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(p["desc"])}">', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', head)
    if slug in globals().get("HI", {}):
        head = head.replace(f'<link rel="canonical" href="{url}">', f'<link rel="canonical" href="{url}">\n'
                            f'<link rel="alternate" hreflang="en" href="{url}">\n'
                            f'<link rel="alternate" hreflang="hi" href="https://filesbolt.com/hi/{slug}/">', 1)
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




# ---------------------------------------------------------------- Hindi versions of the most-searched guides
HI = {
    "merge-pdf": dict(
        title="PDF फ़ाइलें ऑफ़लाइन जोड़ें (Windows)", h1="PDF फ़ाइलों को एक में जोड़ें, बिना अपलोड किए",
        desc="अपने PC पर PDF, फ़ोटो और Word फ़ाइलों को एक PDF में जोड़ें। राइट-क्लिक करें, Merge चुनें, हो गया।",
        intro="File Explorer में फ़ाइलें चुनें, राइट-क्लिक करें और <b>FilesBolt → Merge into one PDF</b> चुनें। जुड़ी हुई PDF "
              "एक-दो सेकंड में उसी फ़ोल्डर में आ जाती है। कुछ भी अपलोड नहीं होता।",
        steps=["File Explorer में PDF, फ़ोटो या Word फ़ाइलें चुनें।", "राइट-क्लिक करें और FilesBolt → Merge into one PDF चुनें।",
               "उसी फ़ोल्डर में Merged.pdf मिलेगी।"],
        faq=[("क्या मैं क्रम बदल सकता हूँ?", "हाँ। FilesBolt खोलें, फ़ाइलें जोड़ें, उन्हें खींचकर क्रम बदलें और Merge पर क्लिक करें।"),
             ("क्या फ़ाइल के आकार की कोई सीमा है?", "नहीं। सब कुछ आपके PC पर चलता है, इसलिए अपलोड की कोई सीमा नहीं है।")]),
    "compress-pdf": dict(
        title="PDF का आकार ऑफ़लाइन छोटा करें", h1="PDF को छोटा करें, बिना अपलोड किए",
        desc="ईमेल के लिए PDF और फ़ोटो अपने PC पर छोटे करें। FilesBolt कॉपी तभी बनाता है जब वह सच में छोटी हो।",
        intro="PDF पर राइट-क्लिक करें और <b>FilesBolt → Compress</b> चुनें। मूल फ़ाइल के पास एक छोटी कॉपी बन जाती है।",
        steps=["File Explorer में PDF पर राइट-क्लिक करें।", "FilesBolt → Compress चुनें।", "छोटी कॉपी मूल फ़ाइल के पास सेव हो जाती है।"],
        faq=[("क्या क्वालिटी खराब होगी?", "टेक्स्ट साफ़ रहता है। PDF के अंदर की तस्वीरें पेज के हिसाब से छोटी की जाती हैं।"),
             ("मेरी फ़ाइल छोटी क्यों नहीं हुई?", "कुछ PDF पहले से ही छोटी होती हैं। FilesBolt कभी बड़ी फ़ाइल नहीं देता।")]),
    "resize-image": dict(
        title="फ़ोटो का साइज़ छोटा करें: 100 KB से 1 MB तक", h1="फ़ॉर्म और ईमेल के लिए फ़ोटो छोटी करें",
        desc="सरकारी फ़ॉर्म, नौकरी के आवेदन और ईमेल के लिए फ़ोटो को 100 KB, 200 KB, 500 KB या 1 MB से कम करें। अपने PC पर।",
        intro="फ़ोटो पर राइट-क्लिक करें और <b>FilesBolt → Resize for email (under 500 KB)</b> चुनें। ऐप में आप 100 KB से कम "
              "भी चुन सकते हैं, जो कई ऑनलाइन फ़ॉर्म माँगते हैं।",
        steps=["फ़ोटो पर राइट-क्लिक करें।", "FilesBolt → Resize for email (under 500 KB) चुनें।", "हर फ़ोटो के पास एक छोटी कॉपी सेव होती है; मूल नहीं बदलती।"],
        faq=[("क्या सरकारी फ़ॉर्म के लिए 100 KB से कम कर सकते हैं?", "हाँ। ऐप में Resize images → Under 100 KB चुनें।"),
             ("क्या मोबाइल की फ़ोटो उलटी हो जाएँगी?", "नहीं। साइज़ बदलने से पहले फ़ोटो सीधी कर दी जाती है।")]),
    "sign-pdf": dict(
        title="PDF पर ऑफ़लाइन हस्ताक्षर करें", h1="अपने PC पर PDF पर हस्ताक्षर करें और भरें",
        desc="PDF में अपने हस्ताक्षर, टेक्स्ट, तारीख और टिक जोड़ें, बिना इंटरनेट के। आपके हस्ताक्षर आपके PC पर ही रहते हैं।",
        intro="PDF पर राइट-क्लिक करें और <b>FilesBolt → Edit and sign</b> चुनें। एक बार हस्ताक्षर बनाएँ, उसे रखें, टेक्स्ट या आज की "
              "तारीख जोड़ें और सेव करें।",
        steps=["PDF पर राइट-क्लिक करें और FilesBolt → Edit and sign चुनें।", "अपने हस्ताक्षर, टेक्स्ट या तारीख जोड़ें।",
               "Save पर क्लिक करें: मूल फ़ाइल के पास _signed कॉपी बन जाती है।"],
        faq=[("क्या मेरे हस्ताक्षर अपलोड होते हैं?", "नहीं। वे सिर्फ़ आपके PC पर सेव रहते हैं।")]),
    "jpg-to-pdf": dict(
        title="फ़ोटो से PDF बनाएँ (JPG, HEIC)", h1="फ़ोटो से PDF बनाएँ, बिना अपलोड किए",
        desc="JPG, PNG और iPhone की HEIC फ़ोटो को अपने PC पर PDF में बदलें। हर फ़ोटो की अलग PDF या सभी की एक PDF।",
        intro="फ़ोटो चुनें, राइट-क्लिक करें और <b>FilesBolt → Convert to PDF</b> चुनें, या सबको एक फ़ाइल में रखने के लिए "
              "<b>Merge into one PDF</b> चुनें।",
        steps=["File Explorer में फ़ोटो चुनें।", "राइट-क्लिक: FilesBolt → Convert to PDF (या Merge into one PDF)।", "PDF फ़ोटो के पास सेव हो जाती है।"],
        faq=[("क्या iPhone की HEIC फ़ोटो चलेंगी?", "हाँ, HEIC के साथ JPG, PNG, WEBP और TIFF भी।")]),
}

if __name__ == "__main__":
    for slug, p in HI.items():
        d = ROOT / "hi" / slug
        d.mkdir(parents=True, exist_ok=True)
        h = page(slug, p).replace('<html lang="en">', '<html lang="hi">', 1)
        h = h.replace(f'<link rel="canonical" href="https://filesbolt.com/{slug}/">',
                      f'<link rel="canonical" href="https://filesbolt.com/hi/{slug}/">\n'
                      f'<link rel="alternate" hreflang="en" href="https://filesbolt.com/{slug}/">\n'
                      f'<link rel="alternate" hreflang="hi" href="https://filesbolt.com/hi/{slug}/">', 1)
        h = h.replace("<h2>How to do it</h2>", "<h2>कैसे करें</h2>").replace("<h2>Why offline?</h2>", "<h2>ऑफ़लाइन क्यों?</h2>")
        h = h.replace("<h2>Questions</h2>", "<h2>सवाल</h2>").replace("Download FilesBolt for Windows", "Windows के लिए FilesBolt डाउनलोड करें")
        h = re.sub(r"<p>Online PDF websites.*?uploads\.</p>", "<p>ऑनलाइन PDF वेबसाइटें आपकी फ़ाइलें अपने सर्वर पर अपलोड करवाती हैं। "
                   "FilesBolt यही काम आपके अपने कंप्यूटर पर करता है, इसलिए आपके दस्तावेज़, ID और बिल कहीं नहीं जाते। "
                   "यह बिना इंटरनेट के भी चलता है।</p>", h, flags=re.S)
        h = re.sub(r"<h2>More things FilesBolt does</h2>\s*<p>.*?</p>", "", h, flags=re.S)
        (d / "index.html").write_text(h, encoding="utf-8")
    print(len(HI), "Hindi pages")

if __name__ == "__main__":  # English pages
    for slug, p in PAGES.items():
        d = ROOT / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page(slug, p), encoding="utf-8")
    print(len(PAGES), "pages")

