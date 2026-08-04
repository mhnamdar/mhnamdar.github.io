# Mohammad-Hossein Namdar — Academic Website

A custom, multi-page academic website inspired by high-end faculty portfolios, with a restrained interactive cosmology hero and clean editorial pages for research, publications, software, talks, CV, contact, and writing.

## What this project is

This is **not** a one-file HTML mockup and it is not tied to an abandoned theme. It has a small, dependency-free static-site engine:

- `data/site.json` — all profile, research, education, project, publication, and software data
- `content/blog/*.md` — blog posts and memories in Markdown
- `templates/base.html` — shared HTML shell
- `scripts/build.py` — generates every route into `dist/`
- `src/assets/css/main.css` — responsive visual system
- `src/assets/js/` — modular animation and interface code
- `.github/workflows/deploy.yml` — automatic GitHub Pages deployment

The generated routes are real separate pages:

`/`, `/about/`, `/research/`, `/projects/`, `/publications/`, `/software/`, `/talks/`, `/blog/`, `/cv/`, and `/contact/`.

## Run locally

```bash
python3 scripts/dev.py
```

Open `http://localhost:8000`. The development server rebuilds when data, content, templates, CSS, or JavaScript changes.

A one-time production build is:

```bash
python3 scripts/check.py
python3 scripts/build.py
```

## Add a blog post or memory

Create `content/blog/my-new-post.md`:

```md
---
title: My title
date: 2026-08-04
category: Memories
tags: [Chile, travel, personal]
excerpt: One sentence shown on the blog card.
featured: false
---

Write the post here in Markdown.
```

Supported categories can be anything. The filter buttons are generated automatically.

## Edit academic content

Edit only `data/site.json`. The same data is reused across the home page, research pages, projects, publications, and printable CV, so facts do not drift across duplicated HTML.

Unknown public links such as ORCID and Google Scholar are intentionally left empty rather than fabricated. Add them when the exact URLs are available.

## Architecture choices

- No package manager and no third-party runtime dependencies
- Python standard-library build system
- ES modules for browser interactions
- Canvas cosmic-web engine isolated in `cosmic-web.js`
- Responsive desktop sidebar and mobile navigation
- Light/dark theme, reduced-motion accessibility, print-ready CV
- SEO metadata, sitemap, robots, RSS, 404 page
- GitHub Pages deployment from generated `dist/`

The animation layer can later be replaced by Three.js without changing the content engine or page templates.
