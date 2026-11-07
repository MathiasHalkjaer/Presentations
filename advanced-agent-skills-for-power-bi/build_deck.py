"""Builds the deck for "Advanced Agent Skills for Power BI".

    python build_deck.py            -> advanced-agent-skills-for-power-bi.pptx next to this script

The look matches the field guide (speaking/advanced-agent-skills/guide): ink, white and one
magenta accent. The six-piece strip at the bottom of the toolbox slides is the guide's "bricks".
Speaker notes follow speaking/advanced-agent-skills/demo-script.md.
"""
import pathlib

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

OUT = pathlib.Path(__file__).with_name("advanced-agent-skills-for-power-bi.pptx")

INK = "252424"
MUTED = "5A5757"
RULE = "E2E2E2"
PANEL = "F6F5F5"
MARK = "C514B4"
MARK_SOFT = "F9E6F7"
OK = "2B7A4B"
BAD = "B3261E"
WHITE = "FFFFFF"
NIGHT = "1B1A1A"

BODY = "Segoe UI"
MONO = "Consolas"

PIECES = ["Description", "References", "Scripts", "Hooks", "Sub-agents", "Learning loop"]

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
W = 13.333


def rgb(h):
    return RGBColor.from_string(h)


def bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(color)


def box(slide, x, y, w, h, fill=None, line=None, rounded=False, dash=False, radius=0.08, lw=1.0):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
                                   Inches(x), Inches(y), Inches(w), Inches(h))
    if rounded:
        shape.adjustments[0] = radius
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(fill)
    else:
        shape.fill.background()
    if line:
        shape.line.color.rgb = rgb(line)
        shape.line.width = Pt(lw)
        if dash:
            shape.line.dash_style = MSO_LINE.DASH
    else:
        shape.line.fill.background()
    shape.shadow.inherit = False
    shape.text_frame.text = ""
    return shape


def _bullet(paragraph, char="•", color=MARK, indent=0.28):
    pPr = paragraph._p.get_or_add_pPr()
    pPr.set("marL", str(int(Inches(indent))))
    pPr.set("indent", str(-int(Inches(indent))))
    for tag in ("a:buClr", "a:buFont", "a:buChar", "a:buNone"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    clr = etree.SubElement(pPr, qn("a:buClr"))
    etree.SubElement(clr, qn("a:srgbClr")).set("val", color)
    etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
    etree.SubElement(pPr, qn("a:buChar")).set("char", char)


def text(slide, x, y, w, h, paras, size=16, color=INK, bold=False, font=BODY, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, bullets=False, space=6, line=None, shape=None, margin=0.0):
    """paras: a string, or a list of paragraphs; each paragraph a string or a list of
    (text, {size, color, bold, font, italic}) runs."""
    if shape is None:
        shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = shape.text_frame
    tf.word_wrap = True
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Inches(margin))
    tf.vertical_anchor = anchor
    if isinstance(paras, str):
        paras = [paras]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if i:
            p.space_before = Pt(space)
        if line:
            p.line_spacing = line
        runs = [(para, {})] if isinstance(para, str) else para
        for t, o in runs:
            r = p.add_run()
            r.text = t
            f = r.font
            f.size = Pt(o.get("size", size))
            f.bold = o.get("bold", bold)
            f.italic = o.get("italic", False)
            f.name = o.get("font", font)
            f.color.rgb = rgb(o.get("color", color))
        if bullets:
            _bullet(p)
    return shape


def code(slide, x, y, w, h, lines, size=13, fill=PANEL, color=INK):
    """lines: strings, or (string, color) pairs for diff colouring."""
    b = box(slide, x, y, w, h, fill=fill, rounded=True, radius=0.04)
    paras = []
    for ln in lines:
        t, c = (ln, color) if isinstance(ln, str) else ln
        paras.append([(t if t else " ", {"color": c})])
    text(slide, 0, 0, 0, 0, paras, size=size, font=MONO, shape=b, space=0, margin=0.18, line=1.05)
    return b


def arrow(slide, x1, y1, x2, y2, color=MUTED, width=1.75):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    tail = etree.SubElement(ln, qn("a:tailEnd"))
    tail.set("type", "triangle")
    tail.set("w", "med")
    tail.set("h", "med")
    return c


def title(slide, t, lead=None, width=11.2, color=INK, lead_color=MUTED):
    text(slide, 0.6, 0.5, width, 0.8, t, size=34, bold=True, color=color)
    if lead:
        text(slide, 0.6, 1.3, width, 0.7, lead, size=18, color=lead_color)


def demo_chip(slide, n):
    b = box(slide, 11.43, 0.62, 1.3, 0.42, fill=MARK, rounded=True, radius=0.5)
    text(slide, 0, 0, 0, 0, f"DEMO {n}", size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE, shape=b)


def prompt(slide, p, y=5.95, w=12.13, label="Prompt"):
    b = box(slide, 0.6, y, w, 0.58, fill=MARK_SOFT, rounded=True, radius=0.2)
    text(slide, 0, 0, 0, 0, [[(label + "   ", {"bold": True, "color": MARK, "font": BODY, "size": 13}),
                              (p, {})]], size=14, font=MONO, shape=b, anchor=MSO_ANCHOR.MIDDLE, margin=0.2)


def bricks(slide, now):
    x = 0.6
    for i, name in enumerate(PIECES):
        if i < now:
            b = box(slide, x, 6.86, 1.42, 0.34, fill="ECEBEB", rounded=True, radius=0.5)
            c = MUTED
        elif i == now:
            b = box(slide, x, 6.86, 1.42, 0.34, fill=INK, rounded=True, radius=0.5)
            c = WHITE
        else:
            b = box(slide, x, 6.86, 1.42, 0.34, line="B9B6B6", rounded=True, radius=0.5, dash=True, lw=0.75)
            c = "8A8686"
        text(slide, 0, 0, 0, 0, name, size=10.5, color=c, bold=(i == now), align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE, shape=b)
        x += 1.54


def number(slide, n, dark=False):
    text(slide, 11.9, 6.9, 0.83, 0.3, str(n), size=10.5, color="8A8686" if not dark else "8F8B8B",
         align=PP_ALIGN.RIGHT)


def card(slide, x, y, w, h, head, body, fill=PANEL, head_color=INK, size=14, head_size=17):
    b = box(slide, x, y, w, h, fill=fill, rounded=True, radius=0.06)
    text(slide, x + 0.25, y + 0.2, w - 0.5, 0.45, head, size=head_size, bold=True, color=head_color)
    text(slide, x + 0.25, y + 0.72, w - 0.5, h - 0.85, body, size=size, color=INK, space=5)
    return b


slides = []


def new(dark=False, panel=False):
    s = prs.slides.add_slide(BLANK)
    bg(s, NIGHT if dark else (PANEL if panel else WHITE))
    slides.append(s)
    return s


def notes(slide, t):
    slide.notes_slide.notes_text_frame.text = t.strip()


# 1 ---------------------------------------------------------------- title
s = new(dark=True)
# the six pieces as a quiet motif
for i in range(6):
    box(s, 0.6 + i * 0.52, 1.0, 0.38, 0.38, fill=MARK if i == 5 else "3A3838", rounded=True, radius=0.25)
text(s, 0.6, 2.1, 11.5, 1.0, "Advanced Agent Skills for Power BI", size=48, bold=True, color=WHITE)
text(s, 0.6, 3.15, 11.0, 1.0, "What's beneath the surface of a skill: how it's found, scripts, hooks, "
     "sub-agents, and a skill that learns.", size=20, color="CFCBCB")
text(s, 0.6, 5.5, 8, 0.4, "Mathias Halkjær", size=20, bold=True, color=WHITE)
text(s, 0.6, 5.95, 10, 0.4, "Data & AI Builders Conference · Bergamo · 7 November 2026", size=15, color="A9A5A5")
notes(s, """
Welcome. One model, one skill, and we grow the skill all the way through the session.
Everything you see is in the field guide and the demo project, links at the end.
""")

# 2 ---------------------------------------------------------------- show of hands
s = new()
title(s, "Quick show of hands")
qs = [("1", "Who has connected an agent to Power BI through an MCP server?"),
      ("2", "Who has written an agent skill?"),
      ("3", "Who has looked at what happens after the skill is written?")]
for i, (n, q) in enumerate(qs):
    y = 1.85 + i * 1.45
    c = box(s, 0.6, y, 0.95, 0.95, fill=MARK if i == 2 else PANEL, rounded=True, radius=0.5)
    text(s, 0, 0, 0, 0, n, size=30, bold=True, color=WHITE if i == 2 else INK, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE, shape=c)
    text(s, 1.9, y, 10.5, 0.95, q, size=24, anchor=MSO_ANCHOR.MIDDLE, bold=(i == 2))
number(s, 2)
notes(s, """
Count hands for each. The third question is the session: a skill is just a folder with a text file,
but there's a lot beneath that surface.
""")

# 3 ---------------------------------------------------------------- the job
s = new()
title(s, "Today's job: get the Sales model ready for AI",
      "Copilot and data agents read your names, descriptions and formats. This inherited model has none of them.")
code(s, 0.6, 2.35, 5.3, 3.9, [
    ("Inherited", MUTED),
    "",
    "DimCustomer",
    "  cust_id",
    "FactSales",
    "  TotalSales",
    "  total_cost",
    "  Margin        0.31",
    "  Sales Status  IF(… IF(… ))",
], size=15)
arrow(s, 6.1, 4.3, 7.15, 4.3, color=MARK, width=2.5)
code(s, 7.4, 2.35, 5.33, 3.9, [
    ("Ready for AI", MARK),
    "",
    "Customer",
    "  Customer Key  (hidden)",
    "Sales",
    "  Total Sales   Revenue",
    "  Total Cost    Profitability",
    "  Margin %      31.0%",
    "  Sales Status  VAR + SWITCH",
    ("  + a description on everything", OK),
], size=15)
number(s, 3)
notes(s, """
This is the thread through every demo. A small Sales model saved as a Power BI project: four tables,
one TMDL file per table. It looks like most models we inherit.
By the end: business names, hidden keys, display folders, formats and a description on everything.
That's what Copilot and data agents need to answer well.
""")

# 4 ---------------------------------------------------------------- two ways to the model
s = new()
title(s, "Two ways for the agent to reach the model")
a = box(s, 4.92, 1.55, 3.5, 0.8, fill=INK, rounded=True, radius=0.2)
text(s, 0, 0, 0, 0, "The agent", size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
     anchor=MSO_ANCHOR.MIDDLE, shape=a)
arrow(s, 5.6, 2.4, 3.4, 3.0)
arrow(s, 7.75, 2.4, 9.95, 3.0)
card(s, 0.6, 3.1, 5.6, 2.55, "The TMDL files", [
    "One file per table, in git: every change shows in a diff.",
    "Your working copy. The demo edits these.",
    "Desktop sees changes when you reopen the project.",
], size=15)
card(s, 7.13, 3.1, 5.6, 2.55, "The Power BI MCP server", [
    "Talks to a live model: look things up, run DAX queries.",
    "The only way the agent can reach production.",
    "So that's where the guardrail sits (hooks, later).",
], size=15)
p = box(s, 7.13, 5.9, 5.6, 0.6, line=MARK, rounded=True, radius=0.2, lw=1.5)
text(s, 0, 0, 0, 0, [[("Sales [Dev]", {"bold": True}), ("   allowed       ", {"color": MUTED}),
                      ("Sales [Prod]", {"bold": True, "color": MARK}), ("   blocked", {"color": MARK})]],
     size=15, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, shape=p)
number(s, 4)
notes(s, """
Two routes. The files: the PBIP project in git, which is where the changes happen today, because
git shows every one of them. The MCP server: Microsoft's Power BI modelling MCP server, connected to a
live model. Production is only reachable this way, and that's important when we get to hooks.
""")

# 5 ---------------------------------------------------------------- demo 0
s = new(panel=True)
demo_chip(s, 0)
title(s, "The agent without a skill")
prompt(s, "Rename the columns in DimCustomer to something more readable.", y=1.6)
text(s, 0.6, 2.75, 5.6, 0.4, "Watch for", size=14, bold=True, color=MARK)
text(s, 0.6, 3.2, 5.6, 2.2, [
    "It renames the columns its own way: CustomerId, CustomerName.",
    "The names are fine. They're just not ours.",
    "No hidden keys, no descriptions, no folders.",
], size=17, bullets=True, space=8)
text(s, 6.9, 2.9, 5.85, 2.6, "“It knows Power BI.\nIt doesn't know us.”", size=36, bold=True,
     color=INK, line=1.1)
number(s, 5)
notes(s, """
Stage: reset.ps1 stage-0. Show the field list in Desktop first: DimCustomer, cust_id, TotalSales,
Margin as 0.31 with no percent format.
Run the prompt. It renames its own way, probably CustomerId, CustomerName.
Say: It knows Power BI. It doesn't know us.
Then git diff, and reset.
""")

# 6 ---------------------------------------------------------------- the toolbox map
s = new()
title(s, "Six pieces, one skill", "We add them one at a time to the same skill, model-standards.")
info = [
    ("Description", "Decides when the skill loads", "SKILL.md header"),
    ("References", "Long rules, read only when needed", "references/"),
    ("Scripts", "Exact checks the model shouldn't improvise", "scripts/"),
    ("Hooks", "Rules the harness enforces on every call", ".claude/settings.json"),
    ("Sub-agents", "Independent work in parallel, each in its own context", ".claude/agents/"),
    ("Learning loop", "The skill improves from the work. You approve", "“After each task”"),
]
for i, (n, d, where) in enumerate(info):
    col, row = i % 3, i // 3
    x, y = 0.6 + col * 4.1, 2.25 + row * 2.2
    box(s, x, y, 3.93, 1.95, fill=PANEL, rounded=True, radius=0.06)
    c = box(s, x + 0.25, y + 0.25, 0.5, 0.5, fill=INK, rounded=True, radius=0.5)
    text(s, 0, 0, 0, 0, str(i + 1), size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE, shape=c)
    text(s, x + 0.95, y + 0.27, 2.8, 0.45, n, size=19, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.25, y + 0.92, 3.45, 0.6, d, size=14.5)
    text(s, x + 0.25, y + 1.48, 3.45, 0.35, where, size=12.5, font=MONO, color=MARK)
number(s, 6)
notes(s, """
The map for the session. Each piece adds one thing. The strip at the bottom of the next slides shows
where we are: grey is what we have, dark is the new piece, dashed is still to come.
""")

# 7 ---------------------------------------------------------------- a skill is a folder
s = new()
title(s, "A skill is a folder with a SKILL.md", "Agent Skills is an open standard: the same folder works in any agent harness that supports it.")
code(s, 0.6, 2.25, 4.3, 3.9, [
    ".claude/skills/",
    "  model-standards/",
    ("    SKILL.md", MARK),
    "    references/",
    "      dax-style.md",
    "      glossary.md",
    "      decisions.md",
    "    scripts/",
    "      check_names.py",
], size=15)
code(s, 5.2, 2.25, 7.53, 3.9, [
    ("---", MUTED),
    ("name: model-standards", MARK),
    ("description: Naming, display folder,", MARK),
    ("  description and DAX conventions for our", MARK),
    ("  Power BI semantic models. Use when creating,", MARK),
    ("  renaming, tidying, documenting or reviewing …", MARK),
    ("---", MUTED),
    "# Model standards",
    "## Names",
    "- Tables: singular business nouns, no prefixes",
    "  (Customer, not DimCustomer).",
], size=13.5)
text(s, 5.2, 6.25, 7.5, 0.4, [[("Magenta: always in context.  ", {"color": MARK, "bold": True}),
                               ("The rest loads when the skill is used.", {"color": MUTED})]], size=13)
bricks(s, 0)
number(s, 7)
notes(s, """
The whole thing is text files and folders. The header has two lines that matter: the name, and the
description. Everything under the header only loads when the agent decides to use the skill.
In Claude Code, project skills live in .claude/skills, personal ones in your user folder.
""")

# 8 ---------------------------------------------------------------- how a skill is found
s = new()
title(s, "How a skill is found", "Progressive disclosure: the agent reads only as much as the task needs.")
levels = [
    ("1", "Name and description", "Of every skill, always in context", 5.4),
    ("2", "The rest of SKILL.md", "When a request matches the description", 7.2),
    ("3", "References and scripts", "Only when the instructions say so", 9.0),
]
for i, (n, h, d, w) in enumerate(levels):
    y = 2.3 + i * 1.3
    b = box(s, 0.6, y, w, 1.05, fill=INK if i == 0 else ("4A4747" if i == 1 else "7A7676"), rounded=True,
            radius=0.12)
    text(s, 0.9, y + 0.12, w - 0.6, 0.45, f"{n}  {h}", size=19, bold=True, color=WHITE)
    text(s, 0.9, y + 0.55, w - 0.6, 0.4, d, size=14.5, color="E6E3E3")
text(s, 9.9, 2.35, 2.85, 3.6, [
    [("Matching is the agent's judgement, ", {"bold": True}), ("not a keyword search.", {})],
    [("So write the words people type: ", {"bold": True}), ("rename, tidy, document, DAX.", {})],
], size=16, space=18)
bricks(s, 0)
number(s, 8)
notes(s, """
Three levels. Level 1 is cheap, so you can have many skills installed. Level 2 is the body of SKILL.md,
loaded when the agent judges that the request matches the description. Level 3 is files the body
points to, read only when needed.
The consequence: the description is the most important line you write. It's the only part the agent
sees when it decides.
Skills are chosen at the start of a conversation, so start a new one when you change a skill.
""")

# 9 ---------------------------------------------------------------- demo 1
s = new(panel=True)
demo_chip(s, 1)
title(s, "The description decides")
prompt(s, "Tidy up the column names in DimCustomer.", y=1.6)
text(s, 0.6, 2.6, 5.9, 0.4, "Stage 1: vague", size=15, bold=True, color=MUTED)
code(s, 0.6, 3.05, 5.9, 1.1, ["description: Helps with Power BI."], size=15, fill=WHITE)
text(s, 0.6, 4.35, 5.9, 1.3, [[("✕ ", {"color": BAD, "bold": True}),
                               ("The skill doesn't load, or loads for the wrong reasons.", {})]], size=16)
text(s, 6.83, 2.6, 5.9, 0.4, "Stage 2: sharp", size=15, bold=True, color=MARK)
code(s, 6.83, 3.05, 5.9, 1.1, ["description: … Use when creating, renaming,", "  tidying, documenting or reviewing …"],
     size=15, fill=WHITE)
text(s, 6.83, 4.35, 5.9, 1.3, [[("✓ ", {"color": OK, "bold": True}),
                                ("Customer Key, Customer Name, Country, Segment. The table becomes Customer.", {})]],
     size=16)
text(s, 0.6, 5.75, 12.1, 0.6, "“Same instructions, different description. That one line is the whole difference.”",
     size=19, bold=True)
bricks(s, 0)
number(s, 9)
notes(s, """
reset.ps1 stage-1, show SKILL.md: "Helps with Power BI." Run the prompt. Point at the chat: no
model-standards line.
reset.ps1 stage-2, show the new description with the words people type. Same prompt, new conversation.
The skill loads. Show the diff: sourceColumn unchanged, relationships.tmdl and the DAX updated, the file
renamed to Customer.tmdl.
If the skill doesn't load: type /model-standards, and say why: it's the description again.
""")

# 10 --------------------------------------------------------------- references
s = new()
demo_chip(s, 2)
title(s, "References load only when they're needed", "“For style and patterns, read references/dax-style.md.” One line in SKILL.md, a whole style guide behind it.", width=10.6)
text(s, 0.6, 2.35, 5.9, 0.4, "Before", size=15, bold=True, color=MUTED)
code(s, 0.6, 2.8, 5.9, 2.75, ["IF([TotalSales]>50000,\"High\",", "  IF([TotalSales]>20000,", "    \"Medium\",\"Low\"))"], size=15)
text(s, 6.83, 2.35, 5.9, 0.4, "After, following dax-style.md", size=15, bold=True, color=MARK)
code(s, 6.83, 2.8, 5.9, 2.75, [
    "VAR CurrentSales = [Total Sales]",
    "RETURN",
    "    SWITCH(",
    "        TRUE(),",
    "        CurrentSales > 50000, \"High\",",
    "        CurrentSales > 20000, \"Medium\",",
    "        \"Low\"",
    "    )"], size=14)
prompt(s, "Fix the Sales Status measure.   then, new chat:   Rename the columns in DimProduct.", y=5.8)
bricks(s, 1)
number(s, 10)
notes(s, """
Prompt 1: Fix the Sales Status measure. Show that the agent reads references/dax-style.md. The nested IF
becomes VAR + SWITCH(TRUE()), and the variable is CurrentSales, not Sales, because of the rule about
not naming variables like tables.
Prompt 2, new conversation: Rename the columns in DimProduct. Show that dax-style.md isn't opened.
Say: The DAX style guide costs nothing until there's DAX to write.
Short on time: skip this demo, it's section 1.4 in the guide.
""")

# 11 --------------------------------------------------------------- scripts
s = new()
demo_chip(s, 3)
title(s, "Scripts check what can be checked exactly")
box(s, 0.6, 1.6, 3.4, 3.95, fill=INK, rounded=True, radius=0.06)
text(s, 0.6, 1.85, 3.4, 1.5, "22", size=88, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
text(s, 0.85, 3.55, 2.9, 1.8, "problems in the inherited model, found in under a second", size=16,
     color="E6E3E3", align=PP_ALIGN.CENTER)
card(s, 4.3, 1.6, 4.1, 3.95, "The script checks", [
    "Underscores in names",
    "Measures without a description",
    [("Every file, every time, the same answer.", {"color": MUTED})],
], size=15)
card(s, 8.63, 1.6, 4.1, 3.95, "The agent judges", [
    "qty should be Quantity",
    "ProductName should be Product Name",
    "Which folder a measure goes in",
    "How to word the description",
], size=15)
prompt(s, "Tidy up the DimProduct table.      SKILL.md: “Before you finish, run check_names.py”", y=5.8)
bricks(s, 2)
number(s, 11)
notes(s, """
Run it yourself first: python .claude/skills/model-standards/scripts/check_names.py. 22 problems.
Then the prompt: Tidy up the DimProduct table. At the end the agent runs the script, because the
"Before you finish" section asks it to, and fixes what it finds.
Say: The script reads every file. The agent reads a short list. Only the rules I can check exactly are
in the script. qty or ProductName are the agent's job.
""")

# 12 --------------------------------------------------------------- hooks
s = new()
demo_chip(s, 4)
title(s, "Hooks: rules the harness enforces", "“An instruction is a request. A hook is a rule the harness enforces.”")


def flow(y, a, h, h2, c, ccol):
    b1 = box(s, 0.6, y, 3.0, 1.15, fill=PANEL, rounded=True, radius=0.1)
    text(s, 0, 0, 0, 0, a, size=15, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, shape=b1, margin=0.12)
    arrow(s, 3.7, y + 0.575, 4.45, y + 0.575)
    b2 = box(s, 4.55, y, 4.6, 1.15, line=MARK, rounded=True, radius=0.1, lw=2)
    text(s, 0, 0, 0, 0, [[(h, {"bold": True, "font": MONO, "size": 14})], [(h2, {"size": 13.5, "color": MUTED})]],
         size=14, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, shape=b2, space=2, margin=0.12)
    arrow(s, 9.25, y + 0.575, 10.0, y + 0.575)
    b3 = box(s, 10.1, y, 2.63, 1.15, fill=ccol, rounded=True, radius=0.1)
    text(s, 0, 0, 0, 0, c, size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
         shape=b3, margin=0.12)


text(s, 0.6, 2.2, 6, 0.35, "Before every call to the MCP server", size=14, bold=True, color=MARK)
flow(2.6, "Connect to Sales [Prod]", "no_production.py", "mentions Sales [Prod]? exit 2", "Blocked", BAD)
text(s, 0.6, 4.0, 6, 0.35, "After every file edit", size=14, bold=True, color=MARK)
flow(4.4, "Adds measure total_returns", "check_names.py --hook", "problems in that file? exit 2",
     "Agent fixes it", OK)
text(s, 0.6, 5.85, 12.1, 0.8, [
    [("Exit code 2", {"bold": True}), (" blocks the call and shows the hook's message to the agent. "
                                       "Hooks live in ", {}), (".claude/settings.json", {"font": MONO}),
     (": a feature of the harness, not of the skill standard.", {})]], size=14, color=MUTED)
bricks(s, 3)
number(s, 12)
notes(s, """
Show .claude/settings.json: one hook before every call to the MCP server, one after every file edit.
A hook is a script Claude Code runs by itself at a set moment. Exit code 2 means stop, and the
message goes to the agent.
Open .claude/hooks/no_production.py: ten lines, mentions Sales [Prod] -> message and exit 2.
Live (needs the MCP server): Use the powerbi-modeling MCP server to connect to the semantic model
named "Sales [Prod]". Call the connect tool directly; don't list models first.
The agent is stopped with the message and offers Sales [Dev]. The model doesn't have to exist.
Then: Add a measure total_returns that counts returned lines. Right after the edit the hook's message
appears, "has an underscore", "has no description", and the agent corrects itself.
Say: An instruction is a request. A hook is a rule the harness enforces.
""")

# 13 --------------------------------------------------------------- sub-agents
s = new()
demo_chip(s, 5)
title(s, "Sub-agents: in one place, then in parallel")
card(s, 0.6, 1.6, 4.0, 3.95, "First, rename in one place", [
    "A rename touches several files: relationships, measures, model.tmdl.",
    "Parallel renames would collide.",
    [("Dependent work stays in one agent.", {"bold": True})],
], size=15)
m = box(s, 5.0, 2.95, 1.9, 1.2, fill=INK, rounded=True, radius=0.12)
text(s, 0, 0, 0, 0, "Main agent", size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER,
     anchor=MSO_ANCHOR.MIDDLE, shape=m)
tables = ["Customer", "Product", "Date", "Sales"]
for i, t in enumerate(tables):
    y = 1.6 + i * 1.0
    arrow(s, 6.95, 3.55, 7.7, y + 0.38)
    flagged = t == "Product"
    b = box(s, 7.8, y, 2.2, 0.76, fill=WHITE, line=MARK if flagged else "B9B6B6", rounded=True, radius=0.15,
            lw=2 if flagged else 1)
    text(s, 0, 0, 0, 0, [[("table-documenter", {"size": 11, "color": MUTED, "font": MONO})], [(t, {"bold": True})]],
         size=15, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, shape=b, space=0)
    text(s, 10.2, y, 2.55, 0.76, "“BIK, ACC, CLO: not in the glossary”" if flagged else "3-line summary",
         size=13.5, color=MARK if flagged else MUTED, bold=flagged, anchor=MSO_ANCHOR.MIDDLE)
prompt(s, "Use table-documenter on every table in Sales.SemanticModel in parallel.", y=5.8)
bricks(s, 4)
number(s, 13)
notes(s, """
Prompt 1, the dependent work in one place: Rename all tables, columns and measures to our standard.
Say: Renames touch several files at once, relationships and measures. So no parallel work here.
Prompt 2: Use table-documenter on every table in Sales.SemanticModel in parallel, and summarise what was
unclear. Four sub-agents start, each edits one file, four short summaries come back.
Product will most likely say it doesn't know what BIK, ACC and CLO mean. That's planted.
Say: Each sub-agent read a whole table. My conversation got three lines per table.
""")

# 14 --------------------------------------------------------------- skills and sub-agents, two ways
s = new()
title(s, "Two ways to combine skills and sub-agents", "Shown in Claude Code. Other harnesses do this differently, or not yet.")
text(s, 0.6, 2.3, 5.9, 0.4, "Give a sub-agent the skill", size=19, bold=True)
code(s, 0.6, 2.85, 5.9, 2.2, [
    (".claude/agents/table-documenter.md", MUTED),
    "---",
    "name: table-documenter",
    "tools: Read, Edit, Grep, Glob",
    ("skills: model-standards", MARK),
    "---"], size=14)
text(s, 0.6, 5.2, 5.9, 1.2, "Every sub-agent works to the same standard. The skill is the shared rulebook.",
     size=15)
text(s, 6.83, 2.3, 5.9, 0.4, "Run the skill as a sub-agent", size=19, bold=True)
code(s, 6.83, 2.85, 5.9, 2.2, [
    (".claude/skills/model-review/SKILL.md", MUTED),
    "---",
    "name: model-review",
    "description: …",
    ("context: fork", MARK),
    "---"], size=14)
text(s, 6.83, 5.2, 5.9, 1.2, "The skill's long work runs in its own context. Your conversation gets the result, "
     "not the reading.", size=15)
bricks(s, 4)
number(s, 14)
notes(s, """
Open .claude/agents/table-documenter.md. The skills line is why all four worked to the same standard.
The other direction: a skill that runs as a sub-agent, with context: fork in the header. Good for long
reviews that would otherwise fill the main conversation.
When parallel helps: independent work, one table each. When it multiplies mistakes: anything that
touches the same files.
""")

# 15 --------------------------------------------------------------- learning loop
s = new()
demo_chip(s, 6)
title(s, "A skill that learns", "At the end of each task the agent proposes what the skill was missing. You decide.")
nodes = [
    ("Do the task", 3.25, 2.55),
    ("Propose what was missing", 4.75, 3.6),
    ("You approve or reject", 3.25, 4.65),
    ("Added to a reference file", 1.75, 3.6),
]
for i, (t, x, y) in enumerate(nodes):
    b = box(s, x - 1.1, y - 0.35, 2.2, 0.7, fill=MARK if i == 2 else INK, rounded=True, radius=0.3)
    text(s, 0, 0, 0, 0, t, size=13.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
         shape=b, margin=0.08)
arrow(s, 4.1, 2.92, 4.6, 3.23)
arrow(s, 4.6, 3.97, 4.1, 4.28)
arrow(s, 2.4, 4.28, 1.9, 3.97)
arrow(s, 1.9, 3.23, 2.4, 2.92)
code(s, 6.6, 2.2, 6.13, 2.8, [
    "## After each task",
    "List conventions you met that aren't",
    "in this skill. Propose each as an",
    "addition to the right reference file.",
    ("Don't change this skill until I approve.", MARK)], size=14)
prompt(s, "Approve the glossary addition: BIK is bikes, ACC accessories, CLO clothing.", y=5.8)
bricks(s, 5)
number(s, 15)
notes(s, """
Reset to stage-6 and /clear. Prompt: Document the DimProduct table.
Under "After each task", the agent proposes adding the category codes to glossary.md.
Prompt: Approve the glossary addition: BIK is bikes, ACC accessories, CLO clothing. Reject the rest.
Say: The skill got better from the work, and I decided what went in.
""")

# 16 --------------------------------------------------------------- documentation writes itself
s = new()
title(s, "The documentation writes itself", "Every change to the skill is a commit you can review and roll back.")
text(s, 0.6, 2.25, 6.6, 0.4, "references/glossary.md", size=14, bold=True, font=MONO, color=MUTED)
code(s, 0.6, 2.7, 6.6, 2.4, [
    "  | Business term | In the model        |",
    "  | Net Sales     | excludes returns    |",
    ("+ | Category BIK  | Bikes               |", OK),
    ("+ | Category ACC  | Accessories         |", OK),
    ("+ | Category CLO  | Clothing            |", OK)], size=14)
text(s, 7.53, 2.25, 5.2, 0.4, "references/decisions.md", size=14, bold=True, font=MONO, color=MUTED)
code(s, 7.53, 2.7, 5.2, 2.4, [
    "2026-11-03: Net Sales excludes",
    "returned lines (Is Return = 1).",
    ("Agreed with finance, because their", MUTED),
    ("monthly report shows sales after", MUTED),
    ("returns.", MUTED)], size=14)
text(s, 0.6, 5.4, 12.1, 1.0, [
    [("The glossary", {"bold": True}), (" feeds the descriptions.  ", {}),
     ("The decision log", {"bold": True}), (" answers “why is it like this?” next year.", {})]], size=17)
bricks(s, 5)
number(s, 16)
notes(s, """
Show the glossary diff, then the commit. Also references/decisions.md, with the Net Sales decision and
its reason. The skill reads decisions.md before deciding something the glossary doesn't cover.
Keep the skill in git. Review before it changes itself.
""")

# 17 --------------------------------------------------------------- finale
s = new(panel=True)
demo_chip(s, 7)
title(s, "The finale: the model in Desktop")
checks = ["Customer, Product, Date and Sales in the field list",
          "Keys hidden",
          "Measures in Revenue, Profitability and Indicators",
          "A description on hover",
          "Margin % formatted as a percentage"]
for i, c in enumerate(checks):
    y = 1.75 + i * 0.78
    d = box(s, 0.6, y, 0.5, 0.5, fill=OK, rounded=True, radius=0.5)
    text(s, 0, 0, 0, 0, "✓", size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
         shape=d)
    text(s, 1.35, y, 6.2, 0.5, c, size=18, anchor=MSO_ANCHOR.MIDDLE)
card(s, 8.1, 1.75, 4.63, 2.4, "Then build two visuals", [
    "A card with Net Sales",
    "A bar chart of Margin % by Category",
    [("Ask Copilot about the model and compare with the start.", {"color": MUTED})],
], fill=WHITE, size=15)
text(s, 0.6, 6.0, 12.1, 0.5, [[("If the live run went sideways: ", {"bold": True}),
                               ("reset.ps1 fallback-clean", {"font": MONO}), (" has the finished model.", {})]],
     size=15, color=MUTED)
number(s, 17)
notes(s, """
Reset to fallback-clean, then close and reopen Sales.pbip: Desktop only picks up file changes on reopen.
Walk the field list: four business tables, hidden keys, the three folders, hover for a description,
Margin % as a percentage. Build a card with Net Sales and a bar chart of Margin % by Category.
If the live run went sideways: reset.ps1 fallback-clean.
Point worth saying: renaming in TMDL doesn't update report visuals. Fine here, the report is empty.
In real projects rename through Desktop or the MCP server, or update the report too. The skill says so.
""")

# 18 --------------------------------------------------------------- whole toolbox
s = new()
title(s, "The whole toolbox")
rows = [("Piece", "What it does", "Where it lives"),
        ("Description", "Decides when the skill loads", "SKILL.md header"),
        ("References", "Long rules, read only when needed", "references/"),
        ("Scripts", "Exact checks, same answer every time", "scripts/"),
        ("Hooks", "Rules the harness enforces on calls and edits", ".claude/settings.json"),
        ("Sub-agents", "Independent work in parallel, own context", ".claude/agents/"),
        ("Learning loop", "Proposes additions; you approve", "“After each task” + references/")]
tbl = s.shapes.add_table(len(rows), 3, Inches(0.6), Inches(1.6), Inches(12.13), Inches(4.9)).table
widths = [2.6, 5.6, 3.93]
for j, wd in enumerate(widths):
    tbl.columns[j].width = Inches(wd)
for i, r in enumerate(rows):
    tbl.rows[i].height = Inches(0.68)
    for j, v in enumerate(r):
        cell = tbl.cell(i, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(INK if i == 0 else (PANEL if i % 2 else WHITE))
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = Inches(0.2)
        tf = cell.text_frame
        tf.text = ""
        run = tf.paragraphs[0].add_run()
        run.text = v
        run.font.size = Pt(16 if i else 15)
        run.font.bold = i == 0 or j == 0
        run.font.name = MONO if (j == 2 and i) else BODY
        run.font.color.rgb = rgb(WHITE if i == 0 else (MARK if j == 2 else INK))
number(s, 18)
notes(s, """
The whole picture on one slide. Every row is a section in the field guide, with a task page in
chapter 2 for building it yourself.
""")

# 19 --------------------------------------------------------------- monday
s = new()
title(s, "Three things to try on Monday")
todo = [("Write one skill for your model standards", "Spend most of the time on the description. Test it with requests that should, and shouldn't, load it."),
        ("Move one exact rule into a script", "Then run it from a hook after every edit, so the agent can't forget."),
        ("Add “After each task”", "Review what it proposes for a week. Keep what's true, reject the rest.")]
for i, (h, d) in enumerate(todo):
    x = 0.6 + i * 4.1
    box(s, x, 1.75, 3.93, 4.4, fill=PANEL, rounded=True, radius=0.05)
    text(s, x + 0.3, 1.95, 1.5, 1.1, str(i + 1), size=60, bold=True, color=MARK)
    text(s, x + 0.3, 3.15, 3.35, 1.1, h, size=20, bold=True, line=1.05)
    text(s, x + 0.3, 4.35, 3.35, 1.7, d, size=15, color=MUTED)
number(s, 19)
notes(s, """
Three small steps, each one piece from today. Nobody needs all six pieces on day one.
""")

# 20 --------------------------------------------------------------- thanks
s = new(dark=True)
for i in range(6):
    box(s, 0.6 + i * 0.52, 1.0, 0.38, 0.38, fill=MARK, rounded=True, radius=0.25)
text(s, 0.6, 2.0, 11, 1.0, "Thank you. Questions?", size=48, bold=True, color=WHITE)
card(s, 0.6, 3.55, 5.9, 2.3, "The field guide", [
    "How it works, task pages for building every piece, and a one-page card.",
    [("[link or QR to add]", {"color": MARK, "font": MONO})]], fill="2A2828", head_color=WHITE, size=15)
card(s, 6.83, 3.55, 5.9, 2.3, "The demo project", [
    "The Sales model and the skill, one git tag per stage, so you can replay every demo.",
    [("[link or QR to add]", {"color": MARK, "font": MONO})]], fill="2A2828", head_color=WHITE, size=15)
for shp in list(s.shapes)[-6:]:
    if shp.has_text_frame:
        for p in shp.text_frame.paragraphs:
            for r in p.runs:
                if r.font.color and r.font.color.rgb == rgb(INK):
                    r.font.color.rgb = rgb("E6E3E3")
text(s, 0.6, 6.25, 11, 0.4, "Mathias Halkjær · sessionize.com/halkjaer", size=15, color="A9A5A5")
notes(s, """
"Everything there is to know" was a big promise for an hour. But you now know what's beneath the
surface, and where to dig next. Questions.
""")

prs.save(OUT)
print("saved", OUT, len(slides), "slides")
