#!/usr/bin/env python3
"""Generate a satirical RetroVerse magazine issue as printable HTML."""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

HEADLINE_PATTERNS = [
    "National Glitter Emergency Declared During '{title}'",
    "{artist} Opens A Department Of Dramatic Pauses",
    "Breaking: '{title}' Causes 700% Increase In Mirror Ball Sales",
    "Experts Confirm '{title}' Is Now A Legal Mood",
    "Congress Investigates Why Everyone Is Humming '{title}'",
    "{artist} Demands A Tax Credit For Fancy Jacket Ownership",
]

CAPTION_PATTERNS = [
    "A downtown dance floor turns into a policy summit while '{title}' loops in the background.",
    "Local citizens freeze mid-argument as {artist} enters with perfect timing and louder shoes.",
    "The band starts measure one, and suddenly every bystander claims to be an interpretive choreographer.",
    "Moments before chaos: one stereo, three disco balls, and a crowd convinced this is civic duty.",
    "A serious strategy meeting collapses when someone yells, 'Play {title} again!'",
]

PULL_QUOTE_PATTERNS = [
    '"If this keeps up, the mayor will have to issue rhythm permits."',
    '"I came for groceries and left with a synchronized dance team."',
    '"Nobody understands the plan, but everyone loves the bass line."',
    '"This is not a trend. This is a fully funded lifestyle decision."',
]

ARTICLE_PARAGRAPH_PATTERNS = [
    (
        "City officials met before dawn to discuss the rapid spread of '{title}'. "
        "By noon, every committee chair was tapping a pencil in tempo and calling it research."
    ),
    (
        "Witnesses say {artist} arrived with excellent posture, suspicious confidence, and exactly one dramatic spotlight. "
        "Within minutes, people who had never danced were offering classes in advanced strut management."
    ),
    (
        "Market analysts report that sales of sequins, platform shoes, and theatrical sighs have climbed all quarter. "
        "One banker described the movement as 'economically confusing but personally uplifting.'"
    ),
    (
        "Critics argue this all may be temporary, but nobody can hear them over the chorus of '{title}'. "
        "In response, readers are invited to send letters, snacks, and any spare bell bottoms to the editorial desk."
    ),
]

YEAR_1978_TOP10_IMAGE_ORDER = [
    "1978_raw_A.png",
    "1978_raw_02.png",
    "1978_raw_03.png",
    "1978_raw_04.png",
    "1978_raw_05.png",
    "1978_raw_06.png",
    "1978_raw_07.png",
    "1978_raw_08.png",
    "1978_raw_09.png",
    "1978_raw_10.png",
]

YEAR_1978_EDITORIAL_CARDS = [
    {
        "image": "1978_raw_J.png",
        "headline": "Editorial Card: Late-Night Listener Mail",
        "caption": "Readers wrote in with disco arguments, emotional weather reports, and stern advice about jacket lapels.",
        "quote": '"The phones rang all night and nobody agreed on the best chorus."',
        "body": "The editorial desk reviewed listener letters and found three recurring themes: devotion to the Top 10, confusion over dance etiquette, and an urgent demand for more dramatic bridge sections.",
    },
    {
        "image": "1978_raw_Q.png",
        "headline": "Editorial Card: Programming Meeting Minutes",
        "caption": "A serious planning session derails when everyone starts ranking intros instead of agenda items.",
        "quote": '"We came for strategy and left with a full side A debate."',
        "body": "In this week's newsroom summit, producers attempted to lock the schedule. The final result was less a calendar and more a spirited referendum on which records deserve permanent repeat status.",
    },
    {
        "image": "1978_raw_K.png",
        "headline": "Editorial Card: Street Style Census",
        "caption": "Field reporters document coordinated jackets, competitive sideburns, and heroic levels of confidence.",
        "quote": '"Fashion was loud, but the playlists were louder."',
        "body": "RetroVerse style correspondents mapped nightlife districts block by block. The data confirms that musical taste and wardrobe choices became indistinguishable by midnight.",
    },
    {
        "image": "1978_raw_R1.png",
        "headline": "Editorial Card: Recap Desk 11-20",
        "caption": "The middle of the chart delivered polished hooks, surprise climbers, and serious radio stamina.",
        "quote": '"If rank 1-10 is fireworks, 11-20 is precision engineering."',
        "body": "Our recap desk highlights songs ranked 11 through 20 as the strategic core of the year. These tracks shaped playlists, influenced format shifts, and kept rotation managers fully employed.",
    },
    {
        "image": "1978_raw_R2.png",
        "headline": "Editorial Card: Recap Desk 21-30",
        "caption": "Deep-chart favorites quietly became neighborhood anthems without asking permission.",
        "quote": '"The back half of the list still knew how to start a party."',
        "body": "Ranks 21 through 30 proved that sustained chart life can outlast hype cycles. These entries built loyal followings and turned ordinary weekends into repeat-listening marathons.",
    },
    {
        "image": "1978_raw_R3.png",
        "headline": "Editorial Card: Recap Desk 31-40",
        "caption": "Late-chart entries brought bold experiments and unforgettable hooks to the finish line.",
        "quote": '"Never underestimate a song that sneaks into the Top 40 and stays in your head."',
        "body": "Our closing-tier roundup covers ranks 31 through 40, where stylistic risks and crossover surprises lived. The numbers may be lower, but the cultural afterlife is unmistakable.",
    },
    {
        "image": "1978_raw_R4.png",
        "headline": "Editorial Card: Year-End Overview",
        "caption": "A full-year snapshot of rhythm, radio drama, and genre collision.",
        "quote": '"1978 was less a playlist and more a full-scale public event."',
        "body": "This final editorial card closes the issue with a year-overview memo. Across all forty ranks, the period blended disco urgency, soft-rock polish, and pop spectacle into one continuous broadcast.",
    },
]


def e(value: object) -> str:
    """HTML-escape helper."""
    return html.escape(str(value), quote=True)


def guess_title_from_filename(image_name: str) -> str:
    stem = Path(image_name).stem
    cleaned = stem.replace("_", " ").replace("-", " ").strip()
    cleaned = " ".join(part for part in cleaned.split() if part)
    return cleaned.title() if cleaned else "Untitled Groove"


def list_images(images_dir: Path) -> list[Path]:
    if not images_dir.exists():
        return []
    return sorted(
        (
            path
            for path in images_dir.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        ),
        key=lambda path: path.name.lower(),
    )


def load_top_40(year: int, project_root: Path, script_dir: Path) -> list[dict]:
    candidates = [
        project_root / f"year_end_top_40_{year}.json",
        project_root / "data" / f"year_end_top_40_{year}.json",
        script_dir / f"year_end_top_40_{year}.json",
    ]

    for candidate in candidates:
        if not candidate.exists():
            continue
        with candidate.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        entries = payload.get("top_40", [])
        if isinstance(entries, list):
            return entries
    return []


def placeholder_headline(title: str, artist: str, index: int) -> str:
    pattern = HEADLINE_PATTERNS[index % len(HEADLINE_PATTERNS)]
    return pattern.format(title=title, artist=artist)


def placeholder_caption(title: str, artist: str, index: int) -> str:
    pattern = CAPTION_PATTERNS[index % len(CAPTION_PATTERNS)]
    return pattern.format(title=title, artist=artist)


def placeholder_pull_quote(index: int) -> str:
    return PULL_QUOTE_PATTERNS[index % len(PULL_QUOTE_PATTERNS)]


def placeholder_article(title: str, artist: str, index: int) -> str:
    paragraphs: list[str] = []
    for offset in range(3):
        pattern = ARTICLE_PARAGRAPH_PATTERNS[(index + offset) % len(ARTICLE_PARAGRAPH_PATTERNS)]
        paragraphs.append(f"<p>{e(pattern.format(title=title, artist=artist))}</p>")
    return "".join(paragraphs)


def editorial_article(text: str) -> str:
    """Render a short editorial block inside the existing feature layout."""
    return f"<p>{e(text)}</p><p>{e('Filed by the RetroVerse editorial desk for archive context and year-end commentary.')}</p>"


def build_cover_page(year: int, top_40: list[dict], issue_stamp: str) -> str:
    if top_40:
        teasers = "".join(
            f"<li>{e(song.get('title', 'Unknown Hit'))} - {e(song.get('artist', 'Unknown Artist'))}</li>"
            for song in top_40[:6]
        )
    else:
        teasers = (
            "<li>The Year Of Maximum Sideburns</li>"
            "<li>Dance Floors Vs. Common Sense</li>"
            "<li>How To Survive A 9-Minute Radio Edit</li>"
        )

    return f"""
<section class="page cover-page">
  <h1 class="masthead">RetroVerse<br/>Magazine</h1>
  <div class="issue-line">Issue Year {e(year)} | Printed {e(issue_stamp)} | Price: 75 cents (ish)</div>
  <div class="subhead">The Unnecessarily Dramatic Guide To Billboard {e(year)}</div>
  <p class="deck">A satirical field report from the front lines of pop music, polyester, and questionable dance decisions.</p>
  <div class="cover-grid">
    <div class="cover-callout">
      <h3>Inside This Issue</h3>
      <ul>{teasers}</ul>
    </div>
    <div class="cover-burst">Bonus Insert:<br/>Top 40 Recap<br/>And Zero Restraint</div>
  </div>
  <div class="footer-note">Cover Story: Rhythm Without Supervision</div>
</section>
""".strip()


def build_editor_page(year: int) -> str:
    return f"""
<section class="page editor-page">
  <div class="section-kicker">Editor's Note</div>
  <h2>Dear Readers, Hold My Mixtape</h2>
  <hr class="mini-rule" />
  <div class="two-column">
    <p>Welcome to the RetroVerse {e(year)} annual issue, assembled under strict deadlines and looser moral standards. This publication exists to honor great songs while asking hard questions, like why every third jacket had lapels wider than a sedan.</p>
    <p>Inside these pages you will find illustrated song cards, dramatic headlines, and reporting that is technically enthusiastic. Every story has been fact checked by someone who once stood near a radio station and nodded confidently.</p>
    <p>As always, our editorial policy is simple: celebrate the music, roast the era gently, and never pass up a chance for a pull quote that sounds like a city council emergency.</p>
    <p>Thank you for reading. Please fold this magazine carefully, pass it to a friend, and pretend the coffee ring on page three is intentional design.</p>
  </div>
  <div class="pull-quote">"We are not here to explain the decade. We are here to document the groove."</div>
  <div class="footer-note">Signed, The RetroVerse Editorial Desk</div>
</section>
""".strip()


def build_feature_pages(year: int, images: list[Path], top_40: list[dict]) -> str:
    if not images:
        return """
<section class="page feature-page">
  <div class="section-kicker">Feature Pages</div>
  <h2>No Card Images Found</h2>
  <p>Add image files to <code>retroverse-magazine/images</code> and re-run <code>generate_magazine.py</code>.</p>
  <div class="footer-note">Feature Desk Awaiting Artwork</div>
</section>
""".strip()

    if year == 1978:
        image_lookup = {image.name: image for image in images}
        pages: list[str] = []

        for idx, song in enumerate(top_40[:10]):
            image_name = YEAR_1978_TOP10_IMAGE_ORDER[idx]
            image_src = f"../images/{e(image_name)}"
            title = str(song.get("title", "Unknown Hit"))
            artist = str(song.get("artist", "Unknown Artist"))
            rank = song.get("rv_rank", idx + 1)
            headline = placeholder_headline(title, artist, idx)
            caption = placeholder_caption(title, artist, idx)
            article_html = placeholder_article(title, artist, idx)
            pull_quote = placeholder_pull_quote(idx)

            if image_name not in image_lookup:
                caption = f"{caption} (Missing image asset: {image_name})"

            page_html = f"""
<section class="page feature-page">
  <div class="section-kicker">Feature Page {idx + 1}</div>
  <h2 class="feature-headline">{e(headline)}</h2>
  <p class="songline">#{e(rank)} in {e(year)}: "{e(title)}" by {e(artist)}</p>
  <div class="feature-card">
    <div class="image-box">
      <img src="{image_src}" alt="Illustrated card for {e(title)} by {e(artist)}" />
    </div>
    <div class="caption-box">{e(caption)}</div>
  </div>
  <div class="pull-quote">{e(pull_quote)}</div>
  <div class="two-column">{article_html}</div>
  <div class="footer-note">Illustrated Archive | RetroVerse</div>
</section>
""".strip()
            pages.append(page_html)

        for offset, card in enumerate(YEAR_1978_EDITORIAL_CARDS):
            page_number = 11 + offset
            image_name = card["image"]
            image_src = f"../images/{e(image_name)}"
            caption = card["caption"]
            if image_name not in image_lookup:
                caption = f"{caption} (Missing image asset: {image_name})"

            page_html = f"""
<section class="page feature-page">
  <div class="section-kicker">Feature Page {page_number}</div>
  <h2 class="feature-headline">{e(card["headline"])}</h2>
  <p class="songline">RetroVerse Editorial Card | Issue {e(year)}</p>
  <div class="feature-card">
    <div class="image-box">
      <img src="{image_src}" alt="Editorial card image for page {page_number}" />
    </div>
    <div class="caption-box">{e(caption)}</div>
  </div>
  <div class="pull-quote">{e(card["quote"])}</div>
  <div class="two-column">{editorial_article(card["body"])}</div>
  <div class="footer-note">Illustrated Archive | RetroVerse</div>
</section>
""".strip()
            pages.append(page_html)

        return "\n".join(pages)

    pages: list[str] = []
    for idx, image_path in enumerate(images):
        song = top_40[idx % len(top_40)] if top_40 else {}
        title = str(song.get("title", guess_title_from_filename(image_path.name)))
        artist = str(song.get("artist", "Mystery Artist"))
        rank = song.get("rv_rank", idx + 1)
        headline = placeholder_headline(title, artist, idx)
        caption = placeholder_caption(title, artist, idx)
        article_html = placeholder_article(title, artist, idx)
        pull_quote = placeholder_pull_quote(idx)
        image_src = f"../images/{e(image_path.name)}"

        page_html = f"""
<section class="page feature-page">
  <div class="section-kicker">Feature Page {idx + 1}</div>
  <h2 class="feature-headline">{e(headline)}</h2>
  <p class="songline">#{e(rank)} in {e(year)}: "{e(title)}" by {e(artist)}</p>
  <div class="feature-card">
    <div class="image-box">
      <img src="{image_src}" alt="Illustrated card for {e(title)} by {e(artist)}" />
    </div>
    <div class="caption-box">{e(caption)}</div>
  </div>
  <div class="pull-quote">{e(pull_quote)}</div>
  <div class="two-column">{article_html}</div>
  <div class="footer-note">Illustrated Archive | RetroVerse</div>
</section>
""".strip()
        pages.append(page_html)

    return "\n".join(pages)


def build_pop_culture_page(year: int, top_40: list[dict]) -> str:
    quick_bits = []
    if top_40:
        for entry in top_40[:8]:
            title = entry.get("title", "Unknown Hit")
            artist = entry.get("artist", "Unknown Artist")
            quick_bits.append(
                f"<li><strong>{e(title)}</strong> by {e(artist)} allegedly caused several neighborhood dance circles and at least one very sincere moustache debate.</li>"
            )
    else:
        quick_bits = [
            "<li>Platform shoes reached heights previously associated with civil engineering.</li>",
            "<li>Three separate people claimed to be the mayor of disco after midnight.</li>",
            "<li>Radio call-ins were 40% requests and 60% emotional monologues.</li>",
        ]

    return f"""
<section class="page pop-culture-page">
  <div class="section-kicker">Pop Culture Section</div>
  <h2>Year {e(year)} In Sideburns, Sequins, And Sudden Opinions</h2>
  <hr class="mini-rule" />
  <div class="two-column">
    <p>The broader culture of {e(year)} moved at the pace of a chart climber with a horn section. Fashion became louder, television became shinier, and every dinner party eventually turned into a debate over who had the superior dance stance.</p>
    <p>Across the country, listeners treated the Top 40 like weekly legislation. New releases were introduced with solemn ceremony, then immediately discussed with the volume and certainty usually reserved for sporting events.</p>
    <p>This section tracks the collateral effects of hit songs: spontaneous choreography, dramatic wardrobe choices, and the rise of deeply committed air-drumming in public settings.</p>
  </div>
  <h3>Quick Hits</h3>
  <ul>{''.join(quick_bits)}</ul>
  <div class="pull-quote">"History remembers the songs. Neighborhoods remember the dance attempts."</div>
  <div class="footer-note">Culture Desk | Special Report</div>
</section>
""".strip()


def build_fake_ad_page() -> str:
    return """
<section class="page fake-ad-page">
  <div class="section-kicker">Fake Advertisement</div>
  <div class="ad-box">
    <h2 class="ad-title">MoodSpray 78</h2>
    <p class="ad-sub">The first aerosol that adds instant chart confidence.</p>
    <p>One spray and your hallway becomes a nightclub entrance. Two sprays and your living room gains a bass line, fake fog, and exactly one person announcing, "Now entering the groove zone."</p>
    <p><strong>Approved by 9 out of 10 fictional DJs.</strong> Side effects may include finger pointing, dramatic jacket flips, and an inability to sit during choruses.</p>
    <p>Order now and receive our bonus booklet: <em>Fifty Emergency Dance Excuses For Work Nights</em>.</p>
  </div>
  <div class="pull-quote">"MoodSpray 78: Because ordinary confidence is for amateurs."</div>
  <div class="footer-note">Paid For By The Society Of Loud Entrances</div>
</section>
""".strip()


def build_letters_page(top_40: list[dict]) -> str:
    titles = [entry.get("title", "that one song") for entry in top_40[:3]]
    if len(titles) < 3:
        titles.extend(["our local jukebox", "late night radio", "a mystery banger"] * 2)

    letters = [
        (
            "From: A Concerned Neighbor",
            f"Please tell your writers to stop describing '{titles[0]}' as a municipal event. My entire block now rehearses choreography after 9 PM.",
        ),
        (
            "From: Proud Dance Captain",
            f"Your coverage of '{titles[1]}' was unfair. We were not loitering. We were conducting field research with glitter and conviction.",
        ),
        (
            "From: Local Record Clerk",
            f"After your last issue, people asked if '{titles[2]}' comes with legal guidance. It does not, but sales are excellent.",
        ),
        (
            "From: The Editorial Desk",
            "Thank you for writing. We hear your concerns and promise to increase both nuance and horn sections in future reporting.",
        ),
    ]

    letter_html = "".join(
        f'<div class="letter-item"><h3>{e(author)}</h3><p>{e(body)}</p></div>' for author, body in letters
    )

    return f"""
<section class="page letters-page">
  <div class="section-kicker">Letters To The Editor</div>
  <h2>Your Mailbag Is Louder Than Our Office Stereo</h2>
  <hr class="mini-rule" />
  <div class="letters-grid">{letter_html}</div>
  <div class="footer-note">Please Keep Writing, We Need Material</div>
</section>
""".strip()


def build_top_40_page(year: int, top_40: list[dict]) -> str:
    if top_40:
        rows = []
        for entry in top_40:
            rows.append(
                "<tr>"
                f"<td>{e(entry.get('rv_rank', ''))}</td>"
                f"<td>{e(entry.get('title', ''))}</td>"
                f"<td>{e(entry.get('artist', ''))}</td>"
                f"<td>{e(entry.get('peak_rank', ''))}</td>"
                f"<td>{e(entry.get('weeks_on_chart', ''))}</td>"
                "</tr>"
            )
        table_body = "".join(rows)
    else:
        table_body = (
            "<tr><td>1</td><td>Placeholder Hit</td><td>Placeholder Artist</td><td>1</td><td>18</td></tr>"
            "<tr><td>2</td><td>Another Placeholder</td><td>Studio Mystery</td><td>2</td><td>16</td></tr>"
        )

    return f"""
<section class="page recap-page">
  <div class="section-kicker">Top 40 Recap</div>
  <h2>Billboard Year-End Snapshot: {e(year)}</h2>
  <p>Data shown below is used for structure and can be replaced or extended when richer AI-authored copy is ready.</p>
  <table>
    <thead>
      <tr>
        <th>Rank</th>
        <th>Song</th>
        <th>Artist</th>
        <th>Peak</th>
        <th>Weeks</th>
      </tr>
    </thead>
    <tbody>{table_body}</tbody>
  </table>
  <div class="footer-note">Data Source: RetroVerse Billboard Archive</div>
</section>
""".strip()


def render_magazine(year: int, script_dir: Path) -> Path:
    images_dir = script_dir / "images"
    output_dir = script_dir / "output"
    template_path = script_dir / "magazine_template.html"
    project_root = script_dir.parent

    output_dir.mkdir(parents=True, exist_ok=True)
    images = list_images(images_dir)
    top_40 = load_top_40(year, project_root, script_dir)
    issue_stamp = datetime.now().strftime("%Y-%m-%d")

    template = template_path.read_text(encoding="utf-8")
    replacements = {
        "YEAR": str(year),
        "COVER_PAGE": build_cover_page(year, top_40, issue_stamp),
        "EDITOR_PAGE": build_editor_page(year),
        "FEATURE_PAGES": build_feature_pages(year, images, top_40),
        "POP_CULTURE_PAGE": build_pop_culture_page(year, top_40),
        "FAKE_AD_PAGE": build_fake_ad_page(),
        "LETTERS_PAGE": build_letters_page(top_40),
        "TOP40_PAGE": build_top_40_page(year, top_40),
    }

    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)

    output_path = output_dir / f"RetroVerse_{year}.html"
    output_path.write_text(rendered, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate RetroVerse satirical magazine HTML.")
    parser.add_argument("--year", type=int, default=1978, help="Billboard year to build the issue for.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    output_path = render_magazine(args.year, script_dir)
    print(f"Generated magazine: {output_path}")


if __name__ == "__main__":
    main()
