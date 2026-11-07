"""Print the guide to PDF (python make_pdf.py advanced-agent-skills-field-guide.pdf). Print version: one column, cover and chapter list first, each part on a new page, light theme. Adapted from the Testing a Data Agent guide."""
import pathlib
import subprocess
import tempfile
import sys

here = pathlib.Path(__file__).parent
page = (here / "advanced-agent-skills-field-guide.html").read_text(encoding="utf-8")
print_css = """
<style>
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
:root { color-scheme: light; }
body { font-size: 10.5pt; padding: 0 !important; }
.book { display: flex !important; flex-direction: column; max-width: none !important; padding: 0 !important; gap: 0 !important; }
nav.toc { order: 2; position: static !important; max-height: none !important; font-size: 11pt; margin: 0 0 0; break-after: page; }
nav.toc ol { gap: 3px !important; }
main { order: 1; display: contents; max-width: none !important; }
.cover { order: 0; padding-top: 70mm; }
.routes { order: 1; margin-bottom: 0 !important; break-after: page; }
.partopen, section.ch { order: 3; }
.partopen { break-before: page; break-after: page; break-inside: avoid; padding-top: 80mm !important; border-top: none !important; }
.partopen h2 { font-size: 30pt !important; }
pre { white-space: pre-wrap; overflow: visible !important; overflow-wrap: anywhere; font-size: 8.3pt !important; }
.task { display: block !important; }
.task > dt { border-top: 1px solid var(--rule) !important; padding: 10px 0 2px !important; break-after: avoid; }
.task > dt:first-of-type { border-top: none !important; padding-top: 0 !important; }
.task > dd { border-top: none !important; padding: 2px 0 8px !important; }
.lead { break-after: avoid; }
.table { overflow: visible !important; }
section.ch { margin-bottom: 22px !important; }
.ch .num, h3, h4 { break-after: avoid; }
pre, table, .why, .like, .card, .lane, .bricks, dl.gloss > *, .steps > li, figure, .casecard, .groups, .ladder > li, .reads { break-inside: avoid; }
figure svg { min-width: 0 !important; }
.sh { break-inside: avoid; }
/* one rule: chapters start a page; short sections stay whole; a figure stays with its lead-in */
#setup, #write, #trigger, #addhook, #learn, #safety, #where, .keep, .pipe, .annot, .groups { break-inside: avoid; }
section.ch { border-bottom: none !important; padding-bottom: 10px !important; margin-bottom: 26px !important; }
.task .table tr:last-child td { border-bottom: none; }
p, li { orphans: 3; widows: 3; }
nav.toc ol { align-content: start; }
nav.toc { display: grid !important; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-template-rows: auto auto; grid-auto-flow: column; column-gap: 24px; }
nav.toc .part { margin-top: 0 !important; }
.card pre { font-size: 8.3pt !important; }
#write, #trigger, #addscript, #aiready, #learn { break-before: page; }
#addscript { margin-bottom: 0 !important; padding-bottom: 0 !important; }
#addscript pre, #addhook pre { font-size: 7.9pt !important; line-height: 1.4; margin-bottom: 8px; }
table { font-size: 9.6pt; }
nav.toc .part { margin-top: 14px; }
tr { break-inside: avoid; }
a { color: var(--ink); text-decoration: none; }
.routes a b { color: var(--ink); }
</style>
"""
html = "<!doctype html><html lang='en'><head><meta charset='utf-8'>" + print_css + "</head><body>" + page + "</body></html>"
# The page's own <style> must come before the print overrides so they win: move it into the head.
start, end = page.index("<style>"), page.index("</style>") + len("</style>")
html = ("<!doctype html><html lang='en'><head><meta charset='utf-8'>" + page[:end] + print_css + "</head><body>"
        + page[end:] + "</body></html>")
src = pathlib.Path(tempfile.gettempdir()) / "advanced-agent-skills-print.html"
src.write_text(html, encoding="utf-8")
out = here / sys.argv[1]
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=15000",
                f"--print-to-pdf={out}", src.as_uri()], check=True, timeout=180)
print(out, out.stat().st_size)
