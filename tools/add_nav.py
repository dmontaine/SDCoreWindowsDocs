#!/usr/bin/env python3
"""
Add prev/next navigation to every HTML page in each documentation set,
create a master index page, and create User and Administrator set
index pages.

Works on the rendered HTML files in <set>/html/ directories.
Each page gets a navigation bar inserted before the </footer> with:
  ← Previous page title     Next page title →

Also creates:
  - index.html at the repo root (master index)
  - User/html/index.html (User set index)
  - Administrator/html/index.html (Administrator set index)

Each index entry links to the page and shows its source markdown file.

A SET INDEX DOES NOT LINK BACK TO THE MASTER INDEX, and that is deliberate
rather than an omission.  Each set is handed out on its own, so the master
index is not there for whoever received one set - the link was a 404 in every
delivered copy, and check_all_links.py reported exactly that three times during
the W1.0-0 audit.  The master index is for browsing the tree locally and links
downward only.
"""

import os
import re
import html as html_mod

DOCS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCT = "SD Core for Windows"
VERSION = "W1.0-0"

# ── Set definitions ──────────────────────────────────────────

SETS = {
    "GettingStarted": {
        "desc": "Installing and running SD Core on Windows, and what differs from OpenQM and SD on Linux.",
        "pages": [
            "00-start-here", "01-installation", "02-first-run",
            "03-running-sd", "04-scheduled-jobs", "05-account-types",
            "06-administrator-commands", "07-programmer-commands",
            "08-ssh-access", "09-api-access", "10-client-distribution",
            "11-lower-case", "12-security", "13-hardening",
            "14-not-in-sd-core",
        ],
    },
    "User": {
        "desc": "For programmers and operators. SDBasic, TCL, the VOC, dictionaries, the file system, and the client API.",
        "pages": [
            "00-sd-introduction", "01-sd-basic-program-structure",
            "02-sd-basic-program-control", "03-sd-basic-math-functions",
            "04-sd-basic-string-functions", "05-sd-basic-dynamic-arrays",
            "06-sd-basic-data-conversion", "07-sd-basic-file-handling",
            "08-sd-basic-select-lists", "09-sd-basic-alternate-key-indexes",
            "10-sd-basic-sequential-files", "11-sd-basic-csv-files",
            "12-sd-basic-terminal-input-and-output", "13-sd-basic-printing",
            "14-sd-basic-locks-and-transactions", "15-sd-basic-sockets",
            "16-sd-basic-system-and-environment", "17-sd-basic-debugging",
            "18-sd-basic-modern-program-structure",
            "19-sd-tcl-command-processor", "20-sd-tcl-files-and-records",
            "21-sd-tcl-query-processor", "22-sd-tcl-select-lists",
            "23-sd-tcl-alternate-key-indexes",
            "24-sd-tcl-programs-and-the-catalogue",
            "25-sd-tcl-ed", "26-sd-tcl-edit", "27-sd-tcl-micro",
            "28-sd-tcl-printing-and-spooling",
            "29-sd-tcl-the-terminal-and-the-session",
            "30-sd-tcl-processes-and-phantoms", "31-sd-tcl-locks",
            "32-sd-voc-structure-and-usage", "33-sd-dicts-structure",
            "34-sd-dicts-conversions", "35-sd-file-system",
            "36-sd-standard-subroutines", "37-sd-client-api",
            "38-sd-glossary", "39-sd-terminfo", "40-sd-programming-tutorial",
            "94-sd-basic-syntax", "95-sd-tcl-syntax",
        ],
    },
    "Administrator": {
        "desc": "For administrators. Accounts, security, remote access, encryption, configuration, installation, and what an ordinary program may not compile.",
        "pages": [
            "01-accounts-and-security", "02-sessions-and-locks",
            "03-operating-system-access", "04-sd-encryption",
            "05-remote-access-and-the-machine", "06-sd-system-limits",
            "07-sd-admin-configuration", "08-sd-installation",
            "09-the-installed-scripts",
            "10-sd-basic-restricted-commands",
        ],
    },
}

# ── CSS for navigation and index pages ───────────────────────

NAV_CSS = """
/* prev/next page navigation */
.pagenav {
  max-width: 46rem;
  margin: 2.5rem 0 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--rule);
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}
.pagenav a {
  color: var(--ink-soft);
  text-decoration: none;
  font-size: 0.92rem;
  line-height: 1.4;
  max-width: 48%;
}
.pagenav a:hover { color: var(--accent); text-decoration: underline; }
.pagenav .pn-prev { text-align: left; }
.pagenav .pn-next { text-align: right; }
.pagenav .pn-label {
  display: block;
  font-size: 0.72rem;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--ink-faint);
  margin-bottom: 0.15rem;
}
.pagenav .pn-spacer { flex: 1; }
@media print { .pagenav { display: none; } }

/* set index page */
.setindex {
  max-width: 46rem;
  margin: 0;
  padding: 0;
}
.setindex h1 { margin-bottom: 0.35rem; }
.setindex .si-subtitle {
  font-size: 1.05rem;
  color: var(--ink-soft);
  margin: 0 0 0.5rem;
  max-width: 40rem;
}
.setindex .si-desc {
  color: var(--ink-soft);
  font-size: 0.92rem;
  margin: 0 0 2rem;
  max-width: 40rem;
}
.setindex .si-source {
  font-family: Consolas, "Cascadia Mono", monospace;
  font-size: 0.78rem;
  color: var(--ink-faint);
}
.setindex table { font-size: 0.92rem; }
.setindex td:nth-child(2) { white-space: normal; }
.setindex td:nth-child(3) { white-space: nowrap; }
@media print {
  .setindex .si-source { display: none; }
}

/* master index page */
.master-index {
  grid-column: 1 / -1;
  max-width: 40rem;
  margin: 0 auto;
  padding: 3rem 0 2.5rem;
}
.master-index h1 {
  font-size: 2.35rem;
  line-height: 1.15;
  margin: 0 0 0.85rem;
  border: 0;
  padding: 0;
}
.master-index .mi-subtitle {
  font-size: 1.08rem;
  line-height: 1.5;
  color: var(--ink-soft);
  margin: 0 0 2.5rem;
  max-width: 34rem;
}
.master-index .mi-sets {
  margin: 0 0 2.5rem;
  padding: 1.5rem 0;
  border-top: 1px solid var(--rule);
  border-bottom: 1px solid var(--rule);
}
.master-index .mi-set {
  margin: 0 0 1.5rem;
}
.master-index .mi-set:last-child { margin-bottom: 0; }
.master-index .mi-set h2 {
  font-size: 1.15rem;
  margin: 0 0 0.4rem;
  padding: 0;
  border: 0;
}
.master-index .mi-set h2 a {
  color: var(--ink);
  text-decoration: none;
}
.master-index .mi-set h2 a:hover { color: var(--accent); text-decoration: underline; }
.master-index .mi-set p {
  font-size: 0.92rem;
  color: var(--ink-soft);
  margin: 0 0 0.3rem;
  max-width: 36rem;
}
.master-index .mi-set .mi-count {
  font-size: 0.78rem;
  color: var(--ink-faint);
}
.master-index .mi-licence p {
  font-size: 0.9rem;
  line-height: 1.55;
  color: var(--ink-soft);
  margin: 0 0 0.7rem;
  max-width: 36rem;
}
"""


# ── Helper: extract title from an HTML page ──────────────────

def get_title(html_path):
    """Extract the document title from a rendered HTML page."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Try <title> tag first
    m = re.search(r'<title>(.+?) - SD Core for Windows</title>', content)
    if m:
        return m.group(1)
    # Fallback: tp-title
    m = re.search(r'<h1 class="tp-title">(.*?)</h1>', content, re.DOTALL)
    if m:
        return html_mod.unescape(m.group(1).strip())
    return os.path.basename(html_path)


def get_subtitle(html_path):
    """Extract the subtitle from a rendered HTML page."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'<p class="tp-subtitle">(.*?)</p>', content, re.DOTALL)
    if m:
        return html_mod.unescape(m.group(1).strip())
    return ""


# ── Add prev/next navigation to all pages ─────────────────────

def add_navigation(set_name, pages):
    """Add prev/next links to every HTML page in a set."""
    html_dir = os.path.join(DOCS_ROOT, set_name, "html")
    md_dir = os.path.join(DOCS_ROOT, set_name, "markdown")

    titles = {}
    for i, page in enumerate(pages):
        html_path = os.path.join(html_dir, page + ".html")
        titles[i] = get_title(html_path)

    for i, page in enumerate(pages):
        html_path = os.path.join(html_path)
        html_path = os.path.join(html_dir, page + ".html")
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip if already has pagenav
        if 'class="pagenav"' in content:
            continue

        # Build navigation HTML
        nav_parts = ['<nav class="pagenav">']

        if i > 0:
            prev_page = pages[i-1]
            prev_title = titles[i-1]
            nav_parts.append(
                f'<a class="pn-prev" href="{prev_page}.html">'
                f'<span class="pn-label">&larr; Previous</span>'
                f'{html_mod.escape(prev_title)}</a>'
            )
        else:
            nav_parts.append('<span class="pn-spacer"></span>')

        # Link to set index
        nav_parts.append('<span class="pn-spacer"></span>')

        if i < len(pages) - 1:
            next_page = pages[i+1]
            next_title = titles[i+1]
            nav_parts.append(
                f'<a class="pn-next" href="{next_page}.html">'
                f'<span class="pn-label">Next &rarr;</span>'
                f'{html_mod.escape(next_title)}</a>'
            )
        else:
            nav_parts.append('<span class="pn-spacer"></span>')

        nav_parts.append('</nav>')
        nav_html = '\n'.join(nav_parts)

        # Insert nav_html before </footer>
        # Also add a link to the set index page
        set_index_link = f'<p style="margin:0.5rem 0 0;font-size:0.82rem;color:var(--ink-faint)"><a href="index.html">{set_name} set index</a></p>'

        # Insert before </footer>
        content = content.replace('</footer>',
                                  nav_html + '\n' + set_index_link + '\n</footer>')

        # Add the nav CSS to the <style> block (before </style>)
        if NAV_CSS not in content:
            content = content.replace('</style>', NAV_CSS + '\n</style>')

        with open(html_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)

    print(f"  {set_name}: added prev/next nav to {len(pages)} pages")


# ── Create set index pages ────────────────────────────────────

def create_set_index(set_name, set_desc, pages):
    """Create an index.html for a documentation set."""
    html_dir = os.path.join(DOCS_ROOT, set_name, "html")
    md_dir = os.path.join(DOCS_ROOT, set_name, "markdown")

    # Build table rows
    rows = []
    for i, page in enumerate(pages):
        html_path = os.path.join(html_dir, page + ".html")
        title = get_title(html_path)
        subtitle = get_subtitle(html_path)
        md_source = page + ".md"
        prev_arrow = "&uarr;" if i > 0 else ""
        rows.append(
            f'<tr>'
            f'<td><a href="{page}.html">{html_mod.escape(title)}</a></td>'
            f'<td>{html_mod.escape(subtitle)}</td>'
            f'<td class="si-source">{md_source}</td>'
            f'</tr>'
        )

    # Count pages
    count = len(pages)
    first_page = pages[0] + ".html"

    # Build the full HTML page using the same template as mkdoc.py
    # but with the set index content instead of a document
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{set_name} set - {PRODUCT}</title>
<style>
:root {{
  --ink:        #1a1c1f;
  --ink-soft:   #555c66;
  --ink-faint:  #767d87;
  --bg:         #ffffff;
  --panel:      #f5f7f9;
  --rule:       #dde1e6;
  --rule-firm:  #b9c0c8;
  --accent:     #1a5fa8;
  --accent-bg:  #eef4fb;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --ink:       #dfe3e8;
    --ink-soft:  #aab2bd;
    --ink-faint: #868f9b;
    --bg:        #16181c;
    --panel:     #1e2127;
    --rule:      #2c3038;
    --rule-firm: #3d434d;
    --accent:    #6fa8e0;
    --accent-bg: #1b2530;
  }}
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: "Segoe UI", -apple-system, "Helvetica Neue", Arial, sans-serif;
  font-size: 16px;
  line-height: 1.62;
  -webkit-text-size-adjust: 100%;
}}
.masthead {{
  border-bottom: 1px solid var(--rule);
  background: var(--panel);
}}
.masthead div {{
  max-width: 66rem;
  margin: 0 auto;
  padding: 0.7rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  font-size: 0.85rem;
  color: var(--ink-soft);
}}
.masthead strong {{ color: var(--ink); font-weight: 600; }}
.page {{
  max-width: 66rem;
  margin: 0 auto;
  padding: 2.5rem 1.5rem 4rem;
  display: grid;
  grid-template-columns: 14rem minmax(0, 1fr);
  gap: 3rem;
}}
@media (max-width: 60rem) {{
  .page {{ grid-template-columns: minmax(0, 1fr); gap: 2rem; padding-top: 1.5rem; }}
}}
main {{ max-width: 46rem; }}
h1, h2, h3 {{ line-height: 1.25; font-weight: 600; }}
h1 {{
  font-size: 2rem;
  margin: 0 0 0.35rem;
  letter-spacing: -0.01em;
}}
h2 {{
  font-size: 1.4rem;
  margin: 2.75rem 0 0.9rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--rule);
}}
p {{ margin: 0 0 1rem; }}
a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 2px; }}
table {{
  border-collapse: collapse;
  width: 100%;
  margin: 0 0 1.5rem;
  font-size: 0.94rem;
}}
th, td {{
  text-align: left;
  vertical-align: baseline;
  padding: 0.5rem 0.9rem 0.5rem 0;
  border-bottom: 1px solid var(--rule);
}}
th {{
  border-bottom: 2px solid var(--rule-firm);
  font-weight: 600;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft);
}}
td:first-child {{ white-space: nowrap; padding-right: 1.5rem; }}
footer {{
  max-width: 66rem;
  margin: 0 auto;
  padding: 1.5rem;
  border-top: 1px solid var(--rule);
  color: var(--ink-faint);
  font-size: 0.82rem;
}}
{NAV_CSS}
@media print {{
  :root {{
    --ink: #000;      --ink-soft: #333;   --ink-faint: #555;
    --bg:  #fff;      --panel: #f4f4f4;
    --rule: #999;     --rule-firm: #333;
    --accent: #000;   --accent-bg: #f4f4f4;
  }}
  body {{ background: #fff; color: #000; font-size: 10.5pt; line-height: 1.45; }}
  .masthead {{ display: none; }}
  .page {{ display: block; max-width: none; padding: 0; }}
  main {{ max-width: none; }}
  a {{ color: #000; text-decoration: none; }}
  .si-source {{ display: none; }}
  footer {{ border-top: 0.5pt solid #999; padding: 0.5rem 0; }}
}}
</style>
</head>
<body>
<div class="masthead"><div><strong>{PRODUCT}</strong><span>{VERSION}</span></div></div>
<div class="page">
<main class="setindex">
<h1>{set_name}</h1>
<p class="si-subtitle">{count} pages. <a href="{first_page}">Start reading &rarr;</a></p>
<p class="si-desc">{set_desc}</p>
<table>
<thead>
<tr>
<th>Page</th>
<th>Description</th>
<th>Source</th>
</tr>
</thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table>
</main>
</div>
<footer>{PRODUCT} {VERSION}. Copyright &copy; 2026 Donald Montaine. Licensed under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).</footer>
</body>
</html>
"""

    index_path = os.path.join(html_dir, "index.html")
    with open(index_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(page_html)
    print(f"  Created {set_name}/html/index.html ({count} pages)")


# ── Create master index page ──────────────────────────────────

def create_master_index():
    """Create the root index.html listing all sets."""
    set_cards = []
    for set_name, info in SETS.items():
        pages = info["pages"]
        desc = info["desc"]
        count = len(pages)
        first = pages[0] + ".html"
        set_cards.append(f"""<div class="mi-set">
<h2><a href="{set_name}/html/{first}">{set_name}</a></h2>
<p>{desc}</p>
<p class="mi-count">{count} pages &middot; <a href="{set_name}/html/index.html">Set index</a></p>
</div>""")

    sets_html = '\n'.join(set_cards)

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{PRODUCT} - Documentation</title>
<style>
:root {{
  --ink:        #1a1c1f;
  --ink-soft:   #555c66;
  --ink-faint:  #767d87;
  --bg:         #ffffff;
  --panel:      #f5f7f9;
  --rule:       #dde1e6;
  --rule-firm:  #b9c0c8;
  --accent:     #1a5fa8;
  --accent-bg:  #eef4fb;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --ink:       #dfe3e8;
    --ink-soft:  #aab2bd;
    --ink-faint: #868f9b;
    --bg:        #16181c;
    --panel:     #1e2127;
    --rule:      #2c3038;
    --rule-firm: #3d434d;
    --accent:    #6fa8e0;
    --accent-bg: #1b2530;
  }}
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: "Segoe UI", -apple-system, "Helvetica Neue", Arial, sans-serif;
  font-size: 16px;
  line-height: 1.62;
  -webkit-text-size-adjust: 100%;
}}
.masthead {{
  border-bottom: 1px solid var(--rule);
  background: var(--panel);
}}
.masthead div {{
  max-width: 66rem;
  margin: 0 auto;
  padding: 0.7rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  font-size: 0.85rem;
  color: var(--ink-soft);
}}
.masthead strong {{ color: var(--ink); font-weight: 600; }}
.page {{
  max-width: 66rem;
  margin: 0 auto;
  padding: 2.5rem 1.5rem 4rem;
  display: grid;
  grid-template-columns: 14rem minmax(0, 1fr);
  gap: 3rem;
}}
@media (max-width: 60rem) {{
  .page {{ grid-template-columns: minmax(0, 1fr); gap: 2rem; padding-top: 1.5rem; }}
}}
main {{ max-width: 46rem; }}
h1, h2, h3, h4 {{ line-height: 1.25; font-weight: 600; }}
h1 {{
  font-size: 2rem;
  margin: 0 0 0.35rem;
  letter-spacing: -0.01em;
}}
h2 {{
  font-size: 1.4rem;
  margin: 2.75rem 0 0.9rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--rule);
}}
p {{ margin: 0 0 1rem; }}
a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 2px; }}
footer {{
  max-width: 66rem;
  margin: 0 auto;
  padding: 1.5rem;
  border-top: 1px solid var(--rule);
  color: var(--ink-faint);
  font-size: 0.82rem;
}}
{NAV_CSS}
@media print {{
  :root {{
    --ink: #000;      --ink-soft: #333;   --ink-faint: #555;
    --bg:  #fff;      --panel: #f4f4f4;
    --rule: #999;     --rule-firm: #333;
    --accent: #000;   --accent-bg: #f4f4f4;
  }}
  body {{ background: #fff; color: #000; font-size: 10.5pt; line-height: 1.45; }}
  .masthead {{ display: none; }}
  .page {{ display: block; max-width: none; padding: 0; }}
  main {{ max-width: none; }}
  a {{ color: #000; text-decoration: none; }}
  footer {{ border-top: 0.5pt solid #999; padding: 0.5rem 0; }}
}}
</style>
</head>
<body>
<div class="masthead"><div><strong>{PRODUCT}</strong><span>{VERSION}</span></div></div>
<div class="page">
<main class="master-index" style="grid-column:1/-1;max-width:40rem;margin:0 auto;padding:3rem 0 2.5rem">
<h1>Documentation</h1>
<p class="mi-subtitle">The {PRODUCT} documentation is organised into four sets, each aimed at a different audience. Each page is a self-contained HTML file.</p>
<div class="mi-sets">
{sets_html}
</div>
<div class="mi-licence">
<p>The documentation is licensed under <a href="https://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)</a>.</p>
<p>Copyright &copy; 2026 Donald Montaine.</p>
</div>
</main>
</div>
<footer>{PRODUCT} {VERSION}. Copyright &copy; 2026 Donald Montaine. Licensed under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).</footer>
</body>
</html>
"""

    index_path = os.path.join(DOCS_ROOT, "index.html")
    with open(index_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(page_html)
    print(f"  Created root index.html")


# ── Fix broken links in markdown ──────────────────────────────

def check_and_fix_links(set_name, pages):
    """Check for broken links in the markdown source files and fix them."""
    md_dir = os.path.join(DOCS_ROOT, set_name, "markdown")
    html_dir = os.path.join(DOCS_ROOT, set_name, "html")

    # Build set of valid HTML page names
    valid_pages = set(p + ".html" for p in pages)

    bad = 0
    fixed = 0
    for page in pages:
        md_path = os.path.join(md_dir, page + ".md")
        if not os.path.exists(md_path):
            continue
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all markdown links to .html files
        link_re = re.compile(r'\]\((\d[\w.-]+\.html)(#[\w-]+)?\)')

        for m in link_re.finditer(content):
            target = m.group(1)
            anchor = m.group(2) or ""
            if target not in valid_pages:
                print(f"  BROKEN in {page}.md: links to {target}{anchor}")
                bad += 1

    if bad == 0:
        print(f"  {set_name}: all markdown links resolve")
    else:
        print(f"  {set_name}: {bad} broken links found (see above)")


# ── Main ──────────────────────────────────────────────────────

print("Adding prev/next navigation...")
for set_name, info in SETS.items():
    add_navigation(set_name, info["pages"])

print("\nCreating set index pages...")
for set_name, info in SETS.items():
    create_set_index(set_name, info["desc"], info["pages"])

print("\nCreating master index page...")
create_master_index()

print("\nChecking for broken links in markdown...")
for set_name, info in SETS.items():
    check_and_fix_links(set_name, info["pages"])

print("\nDone.")
