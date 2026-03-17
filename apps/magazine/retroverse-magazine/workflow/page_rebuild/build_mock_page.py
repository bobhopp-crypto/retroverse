#!/usr/bin/env python3
"""Build a single mock editorial page with text overlays and artwork placeholder."""

from __future__ import annotations

from html import escape

from common import build_parser
from common import load_json
from common import output_path
from common import zone_lookup
from common import write_text


def zone_style(zone: dict[str, object]) -> str:
    return (
        f"left:{zone['x']}%;top:{zone['y']}%;width:{zone['width']}%;height:{zone['height']}%;"
    )


def main() -> None:
    parser = build_parser("Build the mock page layout.")
    args = parser.parse_args()

    brief = load_json(output_path(args.year, args.page_slug, "page_brief.json"))
    zones = zone_lookup(brief["text_safe_zones"])

    title_text = next(block["content"] for block in brief["text_blocks"] if block["id"] == "page_title")
    subtitle_text = next(block["content"] for block in brief["text_blocks"] if block["id"] == "page_subtitle")
    byline_text = next(block["content"] for block in brief["text_blocks"] if block["id"] == "page_byline")
    deck_text = next(block["content"] for block in brief["text_blocks"] if block["id"] == "page_deck")
    body_paragraphs = [block["content"] for block in brief["text_blocks"] if block["role"] == "body"]

    sidebar_html = []
    for block in brief["sidebar_blocks"]:
        items_html = "".join(
            f"<li><strong>{escape(item['label'])}</strong><span>{escape(item['value'])}</span></li>"
            for item in block["items"]
        )
        sidebar_html.append(
            f"""
            <section class="fact-group">
              <h3>{escape(block['title'])}</h3>
              <ul>{items_html}</ul>
            </section>
            """
        )

    body_html = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in body_paragraphs)
    sidebar_combined_html = "".join(sidebar_html)

    title_zone = zones["title_zone"]
    body_zone = zones["body_zone"]
    sidebar_zone = zones["sidebar_zone"]
    footer_zone = zones["footer_zone"]

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(brief['title'])} Mock Page</title>
  <style>
    :root {{
      --paper: #f3e6cb;
      --paper-soft: rgba(250, 242, 226, 0.82);
      --ink: #241b14;
      --ink-soft: #5b4a39;
      --accent: #ac4432;
      --accent-2: #2d6f77;
      --rule: rgba(77, 56, 34, 0.28);
      --shadow: rgba(44, 29, 13, 0.24);
      --safe: rgba(255, 249, 236, 0.66);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 24px;
      background:
        radial-gradient(circle at 20% 15%, rgba(255, 255, 255, 0.24), transparent 34%),
        linear-gradient(180deg, #c9b18b 0%, #af926d 100%);
      font-family: "Iowan Old Style", "Palatino Linotype", serif;
      color: var(--ink);
    }}

    .page {{
      position: relative;
      width: 900px;
      height: 1200px;
      overflow: hidden;
      background: var(--paper);
      border: 1px solid rgba(95, 68, 43, 0.42);
      box-shadow: 0 32px 48px var(--shadow);
    }}

    .page::before {{
      content: "";
      position: absolute;
      inset: 14px;
      border: 1px solid rgba(88, 63, 38, 0.24);
      pointer-events: none;
    }}

    .artwork-layer {{
      position: absolute;
      inset: 0;
      background:
        radial-gradient(circle at 72% 18%, rgba(212, 163, 77, 0.52), transparent 18%),
        radial-gradient(circle at 78% 24%, rgba(182, 70, 53, 0.42), transparent 22%),
        linear-gradient(160deg, rgba(239, 226, 198, 0.92) 10%, rgba(224, 208, 177, 0.74) 42%, rgba(178, 142, 109, 0.78) 100%);
    }}

    .artwork-layer::after {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(90deg, rgba(255, 246, 230, 0.7) 0%, rgba(255, 246, 230, 0.48) 28%, rgba(255, 246, 230, 0.12) 48%, rgba(50, 39, 32, 0.05) 100%),
        repeating-linear-gradient(0deg, rgba(57, 42, 31, 0.03) 0 2px, transparent 2px 4px);
      pointer-events: none;
    }}

    .focal-slot {{
      position: absolute;
      left: 60%;
      top: 9%;
      width: 31%;
      height: 34%;
      border: 2px dashed rgba(78, 54, 31, 0.46);
      background:
        linear-gradient(180deg, rgba(174, 69, 50, 0.34), rgba(63, 76, 82, 0.2)),
        rgba(248, 232, 203, 0.2);
      padding: 18px;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      gap: 10px;
    }}

    .focal-slot strong {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--ink-soft);
    }}

    .focal-slot p {{
      margin: 0;
      font-size: 14px;
      line-height: 1.45;
      color: var(--ink);
    }}

    .safe-zone {{
      position: absolute;
      border: 1.5px dashed rgba(86, 60, 34, 0.34);
      background: rgba(255, 252, 244, 0.17);
      pointer-events: none;
    }}

    .safe-zone span {{
      position: absolute;
      top: 8px;
      left: 10px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: rgba(68, 49, 31, 0.72);
      background: rgba(255, 248, 232, 0.78);
      padding: 2px 5px;
    }}

    .overlay {{
      position: absolute;
      background: var(--paper-soft);
      border: 1px solid var(--rule);
      box-shadow: 0 14px 24px rgba(65, 47, 27, 0.09);
      backdrop-filter: blur(1px);
    }}

    .title-zone {{
      {zone_style(title_zone)}
      padding: 20px 22px 18px;
    }}

    .eyebrow {{
      margin: 0 0 8px;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      color: var(--accent);
    }}

    .page-title {{
      margin: 0;
      font-family: "Baskerville", "Palatino Linotype", serif;
      font-size: 44px;
      line-height: 1.04;
      letter-spacing: 0.01em;
    }}

    .subtitle {{
      margin: 10px 0 0;
      font-size: 18px;
      color: var(--ink-soft);
    }}

    .byline {{
      margin: 10px 0 0;
      font-size: 17px;
      font-style: italic;
      color: var(--accent);
    }}

    .deck {{
      margin: 12px 0 0;
      font-size: 15px;
      line-height: 1.42;
      color: var(--ink-soft);
    }}

    .body-zone {{
      {zone_style(body_zone)}
      padding: 24px;
      column-count: 2;
      column-gap: 30px;
      font-size: 13.8px;
      line-height: 1.48;
      overflow: hidden;
    }}

    .body-zone p {{
      margin: 0 0 12px;
      break-inside: avoid;
    }}

    .sidebar-zone {{
      {zone_style(sidebar_zone)}
      padding: 18px 18px 16px;
      overflow: hidden;
    }}

    .sidebar-zone h2 {{
      margin: 0 0 10px;
      font-size: 17px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--accent);
    }}

    .fact-group + .fact-group {{
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px solid var(--rule);
    }}

    .fact-group h3 {{
      margin: 0 0 8px;
      font-size: 13px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--ink-soft);
    }}

    .fact-group ul {{
      margin: 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 8px;
    }}

    .fact-group li {{
      display: grid;
      gap: 2px;
      font-size: 12.4px;
      line-height: 1.42;
    }}

    .fact-group strong {{
      font-size: 12px;
      color: var(--ink);
    }}

    .footer-zone {{
      {zone_style(footer_zone)}
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 6px 12px;
      font-size: 12px;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--ink-soft);
    }}
  </style>
</head>
<body>
  <article class="page">
    <div class="artwork-layer" aria-hidden="true">
      <div class="focal-slot">
        <strong>Artwork Placeholder</strong>
        <p>Drop approved page-aware illustration here later. Keep the title, body, sidebar, and footer safe zones open.</p>
      </div>
      <div class="safe-zone" style="{zone_style(title_zone)}"><span>title safe zone</span></div>
      <div class="safe-zone" style="{zone_style(body_zone)}"><span>body safe zone</span></div>
      <div class="safe-zone" style="{zone_style(sidebar_zone)}"><span>sidebar safe zone</span></div>
      <div class="safe-zone" style="{zone_style(footer_zone)}"><span>footer safe zone</span></div>
    </div>

    <header class="overlay title-zone" data-zone="title_zone">
      <p class="eyebrow">Page 16 • Screen Feature</p>
      <h1 class="page-title">{escape(title_text)}</h1>
      <p class="subtitle">{escape(subtitle_text)}</p>
      <p class="byline">{escape(byline_text)}</p>
      <p class="deck">{escape(deck_text)}</p>
    </header>

    <section class="overlay body-zone" data-zone="body_zone">
      {body_html}
    </section>

    <aside class="overlay sidebar-zone" data-zone="sidebar_zone">
      <h2>Verified Facts</h2>
      {sidebar_combined_html}
    </aside>

    <footer class="overlay footer-zone" data-zone="footer_zone">
      <span>RetroVerse • {args.year}</span>
      <span>Page {brief['layout_requirements']['page_number']}</span>
    </footer>
  </article>
</body>
</html>
"""

    out_path = output_path(args.year, args.page_slug, "mock_page.html")
    write_text(out_path, html)
    print(out_path)


if __name__ == "__main__":
    main()
