#!/usr/bin/env python3
"""Build the Mohammad-Hossein Namdar academic website.

Dependency-free by design: only the Python standard library is required.
Edit data/site.json and content/blog/*.md, then run:
    python scripts/build.py
The generated website is written to dist/.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

ROOT_DIR = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT_DIR / "dist"
DATA_FILE = ROOT_DIR / "data" / "site.json"
BASE_TEMPLATE = ROOT_DIR / "templates" / "base.html"
BLOG_DIR = ROOT_DIR / "content" / "blog"
ASSET_DIR = ROOT_DIR / "src" / "assets"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def icon(name: str, size: int = 20) -> str:
    paths = {
        "home": '<path d="m3 11 9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M9 20v-6h6v6"/>',
        "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
        "atom": '<circle cx="12" cy="12" r="2"/><path d="M19.1 4.9c2.4 2.4-.5 9.1-6.5 15.1S-.1 24.9 2.3 22.5" transform="translate(0 -1)"/><path d="M4.9 4.9c-2.4 2.4.5 9.1 6.5 15.1s12.7 4.9 10.3 2.5" transform="translate(0 -1)"/><path d="M2 12c0-3.4 6.7-6.2 15-6.2S32 8.6 32 12" transform="scale(.75) translate(0 4)"/>',
        "layers": '<path d="m12 2 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5"/><path d="m3 17 9 5 9-5"/>',
        "file": '<path d="M6 2h8l4 4v16H6z"/><path d="M14 2v5h5"/><path d="M9 13h6M9 17h6"/>',
        "code": '<path d="m8 9-4 3 4 3M16 9l4 3-4 3M14 5l-4 14"/>',
        "mic": '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v4M8 22h8"/>',
        "book": '<path d="M4 4h7a3 3 0 0 1 3 3v13H7a3 3 0 0 0-3 3z"/><path d="M20 4h-3a3 3 0 0 0-3 3v13h3a3 3 0 0 1 3 3z"/>',
        "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V4h8v3M3 12h18M10 12v2h4v-2"/>',
        "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
        "external": '<path d="M14 3h7v7M10 14 21 3"/><path d="M21 14v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h6"/>',
        "arrow": '<path d="M5 12h14M14 7l5 5-5 5"/>',
        "download": '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>',
        "github": '<path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.69c-2.78.6-3.37-1.18-3.37-1.18-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.9 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.64-1.34-2.22-.25-4.56-1.11-4.56-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.64 0 0 .84-.27 2.75 1.02A9.6 9.6 0 0 1 12 6.7c.85 0 1.71.11 2.51.34 1.91-1.29 2.75-1.02 2.75-1.02.55 1.37.2 2.39.1 2.64.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.68-4.57 4.93.36.31.68.92.68 1.85V21c0 .27.18.58.69.48A10 10 0 0 0 12 2Z"/>',
        "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4V8h4v2a5 5 0 0 1 2-2Z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/>',
        "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.42-1.41M17.66 6.34l1.41-1.41"/>',
        "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
        "close": '<path d="m6 6 12 12M18 6 6 18"/>',
        "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/>',
        "pin": '<path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2"/>',
        "filter": '<path d="M4 5h16M7 12h10M10 19h4"/>'
    }
    body = paths.get(name, paths["arrow"])
    return f'<svg class="icon icon-{esc(name)}" width="{size}" height="{size}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{body}</svg>'


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    meta: dict[str, object] = {}
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return meta, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return meta, text
    raw_meta, body = parts[1], parts[2]
    for line in raw_meta.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if value.lower() in {"true", "false"}:
            meta[key] = value.lower() == "true"
        elif value.startswith("[") and value.endswith("]"):
            meta[key] = [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
        else:
            meta[key] = value.strip("'\"")
    return meta, body.strip()


def inline_markdown(text: str) -> str:
    text = esc(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    list_type: str | None = None
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{inline_markdown(' '.join(p.strip() for p in paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    for line in lines + [""]:
        if line.startswith("```"):
            flush_paragraph(); close_list()
            if in_code:
                out.append(f"<pre><code>{esc(chr(10).join(code_lines))}</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        stripped = line.strip()
        if not stripped:
            flush_paragraph(); close_list(); continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph(); close_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>")
            continue
        if stripped.startswith("> "):
            flush_paragraph(); close_list()
            out.append(f"<blockquote>{inline_markdown(stripped[2:])}</blockquote>")
            continue
        ul = re.match(r"^[-*]\s+(.+)$", stripped)
        ol = re.match(r"^\d+\.\s+(.+)$", stripped)
        if ul or ol:
            flush_paragraph()
            wanted = "ul" if ul else "ol"
            if list_type != wanted:
                close_list(); out.append(f"<{wanted}>"); list_type = wanted
            item = (ul or ol).group(1)
            out.append(f"<li>{inline_markdown(item)}</li>")
            continue
        paragraph.append(stripped)
    return "\n".join(out)


def load_posts() -> list[dict[str, object]]:
    posts = []
    for path in sorted(BLOG_DIR.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if meta.get("draft", False):
            continue
        slug = path.stem
        posts.append({**meta, "slug": slug, "body": body, "html": markdown_to_html(body)})
    return sorted(posts, key=lambda p: str(p.get("date", "")), reverse=True)


def nav_html(data: dict, current_path: str) -> str:
    items = []
    for item in data["navigation"]:
        href = item["href"]
        active = current_path == href or (href != "/" and current_path.startswith(href))
        active_attr = ' aria-current="page"' if active else ''
        items.append(
            f'<a class="side-nav__link{" is-active" if active else ""}" href="{esc(href)}"{active_attr}>'
            f'{icon(item["icon"])}<span>{esc(item["label"])}</span></a>'
        )
    profile = data["profile"]
    socials = [
        f'<a href="{esc(profile["github"])}" target="_blank" rel="noreferrer" aria-label="GitHub">{icon("github")}</a>',
        f'<a href="{esc(profile["linkedin"])}" target="_blank" rel="noreferrer" aria-label="LinkedIn">{icon("linkedin")}</a>',
        f'<a href="mailto:{esc(profile["email"])}" aria-label="Email">{icon("mail")}</a>'
    ]
    return f'''
    <aside class="sidebar" id="site-sidebar">
      <a class="monogram" href="/" aria-label="Home"><span>{esc(profile['initials'])}</span><i></i></a>
      <nav class="side-nav" aria-label="Primary navigation">{''.join(items)}</nav>
      <div class="sidebar__social">{''.join(socials)}</div>
    </aside>'''


def mobile_header_html(data: dict) -> str:
    p = data["profile"]
    links = "".join(f'<a href="{esc(item["href"])}">{esc(item["label"])}</a>' for item in data["navigation"])
    return f'''
    <header class="mobile-header">
      <a class="mobile-brand" href="/"><span>{esc(p['initials'])}</span><b>{esc(p['name'])}</b></a>
      <button class="icon-button mobile-menu-button" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu">{icon('menu')}</button>
      <nav class="mobile-menu" id="mobile-menu" aria-label="Mobile navigation">{links}</nav>
    </header>'''


def footer_html(data: dict) -> str:
    p = data["profile"]
    return f'''
    <footer class="site-footer">
      <div>
        <strong>{esc(p['name'])}</strong>
        <span>{esc(p['title'])} · {esc(p['institution'])}</span>
      </div>
      <div class="footer-links">
        <a href="mailto:{esc(p['email'])}">{esc(p['email'])}</a>
        <a href="{esc(p['github'])}" target="_blank" rel="noreferrer">GitHub</a>
        <a href="/feed.xml">RSS</a>
      </div>
      <small>© {datetime.now().year} {esc(p['name'])}. Built for research, writing, and open scientific work.</small>
    </footer>'''


def section_header(kicker: str, title: str, copy: str = "", link: tuple[str, str] | None = None) -> str:
    action = f'<a class="text-link" href="{esc(link[1])}">{esc(link[0])} {icon("arrow", 17)}</a>' if link else ""
    return f'''<div class="section-heading"><div><span class="kicker">{esc(kicker)}</span><h2>{esc(title)}</h2>{f'<p>{esc(copy)}</p>' if copy else ''}</div>{action}</div>'''


def inner_hero(kicker: str, title: str, copy: str, index: str = "01") -> str:
    return f'''
    <header class="inner-hero reveal">
      <div class="inner-hero__index">{esc(index)}</div>
      <div>
        <span class="kicker">{esc(kicker)}</span>
        <h1>{esc(title)}</h1>
        <p>{esc(copy)}</p>
      </div>
      <div class="inner-hero__orb" aria-hidden="true"><i></i><i></i><i></i><b></b></div>
    </header>'''


def home_page(data: dict, posts: list[dict]) -> str:
    p = data["profile"]
    now_rows = "".join(f'<div class="now-row"><span>{esc(row["label"])}</span><strong>{esc(row["value"])}</strong></div>' for row in data["now"])
    featured = data["research"][:3]
    research_cards = "".join(f'''
      <a class="research-mini tilt-card" href="/research/#{esc(r['slug'])}">
        <div class="research-mini__visual"><span>{esc(r['symbol'])}</span><i></i></div>
        <div><span>{esc(r['status'])}</span><h3>{esc(r['title'])}</h3><p>{esc(r['summary'])}</p></div>
      </a>''' for r in featured)
    pubs = "".join(f'''
      <article class="compact-row"><span class="year-badge">{esc(pub['year'])}</span><div><h3>{esc(pub['title'])}</h3><p>{esc(pub['venue'])}</p></div><span class="status-pill">{esc(pub['status'])}</span></article>''' for pub in data["publications"][:3])
    software = "".join(f'''
      <article class="software-row"><div class="software-icon">{icon('code')}</div><div><h3>{esc(item['name'])}</h3><p>{esc(item['description'])}</p></div><span>{esc(item['language'])}</span></article>''' for item in data["software"][:3])
    blog_cards = "".join(post_card(post) for post in posts[:3])
    return f'''
    <section class="home-hero" aria-labelledby="home-title">
      <canvas id="cosmic-web" class="cosmic-canvas" aria-hidden="true"></canvas>
      <div class="hero-grid" aria-hidden="true"></div>
      <div class="hero-copy reveal">
        <span class="kicker">{esc(p['eyebrow'])}</span>
        <h1 id="home-title"><span>Mohammad-Hossein</span><strong>Namdar</strong></h1>
        <h2>{esc(p['title'])} <i></i> Theoretical & Computational Cosmology</h2>
        <p>{esc(p['short_bio'])}</p>
        <div class="hero-actions">
          <a class="button button-primary" href="/research/">Explore my research {icon('arrow')}</a>
          <a class="button" href="/publications/">Publications {icon('arrow')}</a>
          <a class="button" href="/cv/">Curriculum Vitae {icon('arrow')}</a>
        </div>
        <div class="hero-affiliation"><span>{icon('pin')}</span><div><small>Currently at</small><strong>{esc(p['institution'])}</strong><em>{esc(p['department'])} · {esc(p['centre'])}</em></div></div>
      </div>
      <div class="hero-portrait reveal" aria-hidden="true">
        <div class="portrait-system cosmic-field" data-parallax>
            <div class="orbit orbit-a"></div>
            <div class="orbit orbit-b"></div>
            <div class="orbit orbit-c"></div>
            <div class="star-core"></div>
            <div class="nebula-cloud nebula-a"></div>
            <div class="nebula-cloud nebula-b"></div>
            <div class="nebula-cloud nebula-c"></div>

            <div class="field-caption">
              <span>INTERACTIVE COSMIC FIELD</span>
              <strong>Move the cursor to perturb the web</strong>
            </div>
          </div>
        </div>
      <aside class="now-panel reveal"><div class="panel-title"><span>NOW</span><i></i></div>{now_rows}</aside>
      <a class="top-cv-link" href="/cv/">{icon('file')} Curriculum Vitae</a>
      <a class="top-contact-link" href="/contact/">Get in touch {icon('arrow')}</a>
    </section>

    <section class="dashboard-grid section-pad">
      <article class="glass-panel about-panel reveal">
        <div class="panel-heading">{icon('user')}<h2>About me</h2></div>
        <p>{esc(p['long_bio'])}</p>
        <div class="about-orbit" aria-hidden="true"><i></i><i></i><b></b></div>
        <a class="text-link" href="/about/">Full profile {icon('arrow',17)}</a>
      </article>
      <article class="glass-panel featured-panel reveal">
        <div class="panel-heading">{icon('atom')}<h2>Featured research</h2></div>
        <div class="research-mini-grid">{research_cards}</div>
        <a class="text-link" href="/research/">View all research {icon('arrow',17)}</a>
      </article>
      <article class="glass-panel faculty-panel reveal">
        <div class="panel-heading">{icon('layers')}<h2>Current at UC Chile</h2></div>
        <div class="institution-mark"><span>UC</span><div><strong>{esc(p['department'])}</strong><em>{esc(p['centre'])}</em></div></div>
        <p>PhD research and computational astrophysics in Santiago, including current collaboration with Rolando Dünner and Gaspar Galaz.</p>
        <div class="faculty-tags"><span>Simulation</span><span>Cosmology</span><span>Scientific computing</span></div>
      </article>
    </section>

    <section class="home-section section-pad reveal">
      {section_header('SCHOLARLY WORK', 'Selected manuscripts & research outputs', 'Current work, research manuscripts, and thesis-level contributions.', ('All publications', '/publications/'))}
      <div class="panel-list">{pubs}</div>
    </section>

    <section class="home-split section-pad">
      <div class="reveal">
        {section_header('METHODS', 'Software & computational work', 'Research code and reproducible scientific workflows.', ('Software page', '/software/'))}
        <div class="panel-list">{software}</div>
      </div>
      <aside class="contact-card reveal">
        <span class="kicker">COLLABORATION</span><h2>Let’s discuss cosmology.</h2><p>{esc(p['availability'])}</p>
        <a class="button button-primary" href="mailto:{esc(p['email'])}">Send an email {icon('arrow')}</a>
        <small>{esc(p['email'])}</small>
        <div class="contact-orbits" aria-hidden="true"><i></i><i></i><b></b></div>
      </aside>
    </section>

    <section class="home-section section-pad reveal">
      {section_header('NOTES & MEMORIES', 'Blog', 'Research notes, academic life, personal writing, and memories.', ('Open the blog', '/blog/'))}
      <div class="blog-grid">{blog_cards}</div>
    </section>'''


def about_page(data: dict) -> str:
    p = data["profile"]
    edu = "".join(timeline_item(item["period"], item["degree"], item["institution"], item["detail"]) for item in data["education"])
    exp = "".join(timeline_item(item["period"], item["role"], item["institution"], item["detail"]) for item in data["experience"])
    skills = "".join(f'<span>{esc(s)}</span>' for s in data["skills"])
    return inner_hero("PROFILE", "About", "A research profile shaped by cosmology, gravity, computation, and the physics of cosmic structure.", "01") + f'''
    <section class="content-layout section-pad">
      <article class="prose-card reveal">
        <span class="kicker">BIOGRAPHY</span><h2>Researching the evolving Universe</h2>
        <p>{esc(p['long_bio'])}</p>
        <p>My academic path began in physics at Isfahan University of Technology, continued through an MSc in gravity and cosmology at Shahid Beheshti University, and now extends into doctoral research at UC Chile. Across these stages, the recurring question has been how mathematical structure becomes observable cosmic structure.</p>
        <p>I value research that is theoretically explicit, computationally reproducible, and honest about the limits of data and approximations.</p>
      </article>
      <aside class="fact-card reveal"><span class="kicker">AT A GLANCE</span><dl><dt>Position</dt><dd>{esc(p['role'])}</dd><dt>Institution</dt><dd>{esc(p['institution'])}</dd><dt>Research units</dt><dd>{esc(p['department'])}<br>{esc(p['centre'])}</dd><dt>Location</dt><dd>{esc(p['location'])}</dd><dt>Email</dt><dd><a href="mailto:{esc(p['email'])}">{esc(p['email'])}</a></dd></dl></aside>
    </section>
    <section class="two-column section-pad">
      <div class="reveal">{section_header('ACADEMIC PATH', 'Education')}<div class="timeline">{edu}</div></div>
      <div class="reveal">{section_header('CURRENT WORK', 'Experience')}<div class="timeline">{exp}</div></div>
    </section>
    <section class="home-section section-pad reveal">{section_header('TOOLKIT', 'Research interests & methods')}<div class="skill-cloud">{skills}</div></section>'''


def timeline_item(period: str, title: str, institution: str, detail: str) -> str:
    return f'''<article class="timeline-item"><span>{esc(period)}</span><div><h3>{esc(title)}</h3><strong>{esc(institution)}</strong><p>{esc(detail)}</p></div></article>'''


def research_page(data: dict) -> str:
    cards = []
    for idx, r in enumerate(data["research"], 1):
        methods = "".join(f'<span>{esc(m)}</span>' for m in r["methods"])
        collaborators = ", ".join(r["collaborators"])
        cards.append(f'''
        <article class="research-detail reveal" id="{esc(r['slug'])}">
          <div class="research-detail__number">0{idx}</div>
          <div class="research-detail__symbol"><span>{esc(r['symbol'])}</span><i></i><i></i></div>
          <div class="research-detail__body"><span class="status-line">{esc(r['status'])}</span><h2>{esc(r['title'])}</h2><p class="lead">{esc(r['summary'])}</p><p>{esc(r['details'])}</p><div class="tag-list">{methods}</div><footer><strong>Collaborators / research context</strong><span>{esc(collaborators)}</span></footer></div>
        </article>''')
    return inner_hero("RESEARCH", "Research programme", "Current work in dark-sector cosmology, nonlinear gravity, structure formation, and computational astrophysics.", "02") + f'<section class="research-stack section-pad">{"".join(cards)}</section>'


def projects_page(data: dict) -> str:
    cards = "".join(f'''
    <a class="project-card tilt-card reveal" href="{esc(p['href'])}">
      <div class="project-card__meta"><span>{esc(p['type'])}</span><b>{esc(p['year'])}</b></div><h2>{esc(p['title'])}</h2><p>{esc(p['description'])}</p><div class="tag-list">{''.join(f'<span>{esc(t)}</span>' for t in p['tags'])}</div><div class="project-arrow">Open project {icon('arrow',18)}</div>
    </a>''' for p in data["projects"])
    return inner_hero("PROJECTS", "Selected projects", "Active research, ongoing manuscripts, and carefully labeled exploratory directions.", "03") + f'''
    <section class="project-grid section-pad">{cards}</section>
    <section class="statement-band reveal" id="future-directions"><span class="kicker">FUTURE DIRECTIONS</span><h2>From halo assembly to observable dark-matter signatures</h2><p>Exploratory ideas are kept separate from active manuscripts. The site never presents a proposal as a completed result.</p></section>'''


def publications_page(data: dict) -> str:
    rows = "".join(f'''
    <article class="publication-card reveal"><div class="publication-year">{esc(pub['year'])}</div><div><div class="publication-status">{esc(pub['status'])}</div><h2>{esc(pub['title'])}</h2><p class="authors">{esc(pub['authors'])}</p><strong>{esc(pub['venue'])}</strong></div></article>''' for pub in data["publications"])
    return inner_hero("PUBLICATIONS", "Scholarly work", "Manuscripts, research work in development, and thesis contributions—without fabricated journal records or citation metrics.", "04") + f'''
    <section class="publication-list section-pad">{rows}</section>
    <section class="note-box reveal"><strong>Publication policy</strong><p>Items are labeled by their actual status. Links to arXiv, DOI, code, and data can be added in <code>data/site.json</code> as soon as they are public.</p></section>'''


def software_page(data: dict) -> str:
    cards = "".join(f'''
    <article class="software-card reveal"><div class="software-card__top"><span>{icon('code',24)}</span><b>{esc(item['status'])}</b></div><h2>{esc(item['name'])}</h2><p>{esc(item['description'])}</p><footer><span>{esc(item['language'])}</span></footer></article>''' for item in data["software"])
    return inner_hero("SOFTWARE", "Scientific code & methods", "Research implementations, analysis workflows, and the code architecture behind this website.", "05") + f'''
    <section class="software-grid section-pad">{cards}</section>
    <section class="github-band reveal"><div><span class="kicker">OPEN WORK</span><h2>Code evolves with the research.</h2><p>Public repositories will be linked here when documentation and reproducibility checks are ready.</p></div><a class="button button-primary" href="{esc(data['profile']['github'])}" target="_blank" rel="noreferrer">GitHub profile {icon('external')}</a></section>'''


def talks_page(data: dict) -> str:
    talks = "".join(f'''<article class="talk-card reveal"><time>{esc(t['year'])}</time><div><h2>{esc(t['title'])}</h2><strong>{esc(t['event'])}</strong><p>{esc(t['description'])}</p></div></article>''' for t in data["talks"])
    return inner_hero("TALKS", "Talks & presentations", "An archive for thesis defenses, seminars, conference talks, posters, and public outreach.", "06") + f'''
    <section class="talk-list section-pad">{talks}</section>
    <section class="note-box reveal"><strong>Archive in progress</strong><p>Only confirmed presentations are listed. Slides, posters, and recordings can be added directly to this page through <code>data/site.json</code>.</p></section>'''


def post_card(post: dict) -> str:
    tags = "".join(f'<span>{esc(t)}</span>' for t in post.get("tags", []))
    return f'''
    <a class="blog-card tilt-card" href="/blog/{esc(post['slug'])}/" data-category="{esc(post.get('category','Notes'))}">
      <div class="blog-card__top"><span>{esc(post.get('category','Notes'))}</span><time>{esc(post.get('date',''))}</time></div>
      <h3>{esc(post.get('title','Untitled'))}</h3><p>{esc(post.get('excerpt',''))}</p><div class="blog-tags">{tags}</div><strong>Read note {icon('arrow',17)}</strong>
    </a>'''


def blog_page(posts: list[dict]) -> str:
    categories = sorted({str(p.get("category", "Notes")) for p in posts})
    filters = '<button class="is-active" data-blog-filter="all">All</button>' + "".join(f'<button data-blog-filter="{esc(c)}">{esc(c)}</button>' for c in categories)
    cards = "".join(post_card(p) for p in posts)
    return inner_hero("BLOG", "Notes, academic life & memories", "A flexible writing space for technical notes, personal essays, photographs, and moments beyond the formal CV.", "07") + f'''
    <section class="blog-toolbar reveal"><div>{icon('filter',18)}<span>Filter by category</span></div><div class="blog-filters">{filters}</div></section>
    <section class="blog-grid blog-index-grid section-pad">{cards}</section>'''


def blog_post_page(post: dict) -> str:
    tags = "".join(f'<span>{esc(t)}</span>' for t in post.get("tags", []))
    return f'''
    <article class="article-shell">
      <header class="article-header reveal"><a href="/blog/">← Back to all notes</a><span class="kicker">{esc(post.get('category','Notes'))}</span><h1>{esc(post.get('title','Untitled'))}</h1><p>{esc(post.get('excerpt',''))}</p><div><time>{esc(post.get('date',''))}</time><div class="blog-tags">{tags}</div></div></header>
      <div class="article-body reveal">{post['html']}</div>
      <footer class="article-footer"><span>Written by Mohammad-Hossein Namdar</span><a href="mailto:mnamdar0@estudiante.uc.cl">Discuss this note {icon('arrow',17)}</a></footer>
    </article>'''


def cv_page(data: dict) -> str:
    p = data["profile"]
    edu = "".join(f'<article><time>{esc(x["period"])}</time><div><h3>{esc(x["degree"])}</h3><strong>{esc(x["institution"])}</strong><p>{esc(x["detail"])}</p></div></article>' for x in data["education"])
    exp = "".join(f'<article><time>{esc(x["period"])}</time><div><h3>{esc(x["role"])}</h3><strong>{esc(x["institution"])}</strong><p>{esc(x["detail"])}</p></div></article>' for x in data["experience"])
    pubs = "".join(f'<li><strong>{esc(x["title"])}</strong><span>{esc(x["authors"])}</span><em>{esc(x["venue"])} · {esc(x["status"])}</em></li>' for x in data["publications"])
    skills = " · ".join(data["skills"])
    return f'''
    <section class="cv-actions no-print"><a href="/">{icon('arrow',17)} Back to website</a><button class="button button-primary" type="button" data-print-cv>{icon('download')} Print / Save as PDF</button></section>
    <article class="cv-sheet">
      <header><div><span class="kicker">CURRICULUM VITAE</span><h1>{esc(p['name'])}</h1><p>{esc(p['title'])} · {esc(p['institution'])}</p></div><div class="cv-contact"><a href="mailto:{esc(p['email'])}">{esc(p['email'])}</a><span>{esc(p['location'])}</span><a href="{esc(p['github'])}">github.com/mhnamdar</a></div></header>
      <section><h2>Profile</h2><p>{esc(p['long_bio'])}</p></section>
      <section><h2>Research experience</h2><div class="cv-timeline">{exp}</div></section>
      <section><h2>Education</h2><div class="cv-timeline">{edu}</div></section>
      <section><h2>Research works</h2><ol class="cv-publications">{pubs}</ol></section>
      <section><h2>Research interests & methods</h2><p>{esc(skills)}</p></section>
    </article>'''


def contact_page(data: dict) -> str:
    p = data["profile"]
    subject = quote("Research collaboration / academic inquiry")
    return inner_hero("CONTACT", "Get in touch", "For research collaborations, seminars, academic discussions, and questions about my work.", "08") + f'''
    <section class="contact-layout section-pad">
      <article class="contact-main reveal"><span class="kicker">EMAIL</span><h2>{esc(p['email'])}</h2><p>{esc(p['availability'])}</p><a class="button button-primary" href="mailto:{esc(p['email'])}?subject={subject}">Compose email {icon('arrow')}</a></article>
      <aside class="contact-details reveal"><div>{icon('pin')}<span><small>Based in</small><strong>{esc(p['location'])}</strong></span></div><div>{icon('layers')}<span><small>Affiliations</small><strong>{esc(p['department'])}<br>{esc(p['centre'])}</strong></span></div><div>{icon('github')}<span><small>Code</small><a href="{esc(p['github'])}" target="_blank" rel="noreferrer">github.com/mhnamdar</a></span></div><div>{icon('linkedin')}<span><small>Professional profile</small><a href="{esc(p['linkedin'])}" target="_blank" rel="noreferrer">LinkedIn</a></span></div></aside>
    </section>'''


def render_page(data: dict, content: str, path: str, title: str, description: str, slug: str) -> str:
    template = BASE_TEMPLATE.read_text(encoding="utf-8")
    depth = 0 if path == "/" else len([x for x in path.strip("/").split("/") if x])
    root = "../" * depth
    canonical = data["site"]["url"].rstrip("/") + path
    replacements = {
        "{{TITLE}}": esc(title), "{{DESCRIPTION}}": esc(description), "{{CANONICAL}}": esc(canonical),
        "{{SITE_URL}}": esc(data["site"]["url"]), "{{PAGE_SLUG}}": esc(slug), "{{ROOT}}": root,
        "{{SIDEBAR}}": nav_html(data, path), "{{MOBILE_HEADER}}": mobile_header_html(data),
        "{{CONTENT}}": content, "{{FOOTER}}": footer_html(data)
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def write_route(route: str, html_text: str) -> None:
    if route == "/":
        target = DIST_DIR / "index.html"
    else:
        target = DIST_DIR / route.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html_text, encoding="utf-8")


def build_feed(data: dict, posts: list[dict]) -> str:
    base = data["site"]["url"].rstrip("/")
    items = []
    for post in posts[:20]:
        url = f"{base}/blog/{post['slug']}/"
        items.append(f'''<item><title>{esc(post.get('title',''))}</title><link>{url}</link><guid>{url}</guid><pubDate>{esc(post.get('date',''))}</pubDate><description>{esc(post.get('excerpt',''))}</description></item>''')
    return f'''<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{esc(data['site']['title'])} — Notes</title><link>{base}/blog/</link><description>{esc(data['site']['description'])}</description>{''.join(items)}</channel></rss>'''


def build() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    posts = load_posts()
    if DIST_DIR.exists(): shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)
    shutil.copytree(ASSET_DIR, DIST_DIR / "assets")

    pages = [
        ("/", home_page(data, posts), f"{data['profile']['name']} — Cosmology & Astrophysics", data["site"]["description"], "home"),
        ("/about/", about_page(data), "About — Mohammad-Hossein Namdar", "Biography, education, and research profile of Mohammad-Hossein Namdar.", "about"),
        ("/research/", research_page(data), "Research — Mohammad-Hossein Namdar", "Research in matter-diffusion cosmology, interacting dark energy, Monge–Ampère gravity, and computational astrophysics.", "research"),
        ("/projects/", projects_page(data), "Projects — Mohammad-Hossein Namdar", "Selected current and exploratory cosmology research projects.", "projects"),
        ("/publications/", publications_page(data), "Publications — Mohammad-Hossein Namdar", "Manuscripts, thesis work, and scholarly outputs.", "publications"),
        ("/software/", software_page(data), "Software — Mohammad-Hossein Namdar", "Scientific software, research code, and computational methods.", "software"),
        ("/talks/", talks_page(data), "Talks — Mohammad-Hossein Namdar", "Talks, presentations, posters, and outreach.", "talks"),
        ("/blog/", blog_page(posts), "Blog — Mohammad-Hossein Namdar", "Research notes, academic life, personal writing, and memories.", "blog"),
        ("/cv/", cv_page(data), "Curriculum Vitae — Mohammad-Hossein Namdar", "Curriculum vitae of Mohammad-Hossein Namdar.", "cv"),
        ("/contact/", contact_page(data), "Contact — Mohammad-Hossein Namdar", "Contact Mohammad-Hossein Namdar for research and academic collaboration.", "contact")
    ]
    for route, content, title, desc, slug in pages:
        write_route(route, render_page(data, content, route, title, desc, slug))
    for post in posts:
        route = f"/blog/{post['slug']}/"
        write_route(route, render_page(data, blog_post_page(post), route, f"{post.get('title')} — Mohammad-Hossein Namdar", str(post.get("excerpt", "")), "article"))

    all_routes = [x[0] for x in pages] + [f"/blog/{p['slug']}/" for p in posts]
    urls = "".join(f"<url><loc>{data['site']['url'].rstrip('/')}{route}</loc></url>" for route in all_routes)
    (DIST_DIR / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', encoding="utf-8")
    (DIST_DIR / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {data['site']['url']}/sitemap.xml\n", encoding="utf-8")
    (DIST_DIR / "feed.xml").write_text(build_feed(data, posts), encoding="utf-8")
    (DIST_DIR / ".nojekyll").write_text("", encoding="utf-8")
    not_found = render_page(data, inner_hero("404", "Page not found", "The page may have moved. Return to the research homepage.", "404") + '<section class="center-action"><a class="button button-primary" href="/">Return home</a></section>', "/404/", "404 — Page not found", "Page not found.", "not-found")
    # GitHub Pages expects 404.html at the artifact root, so its assets are root-relative.
    not_found = not_found.replace('../assets/', 'assets/').replace('../feed.xml', 'feed.xml')
    (DIST_DIR / "404.html").write_text(not_found, encoding="utf-8")
    print(f"Built {len(pages) + len(posts)} pages in {DIST_DIR}")


if __name__ == "__main__":
    build()
