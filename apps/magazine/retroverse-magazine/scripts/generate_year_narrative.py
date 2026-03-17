#!/usr/bin/env python3
"""Build a data-grounded editorial narrative plan from year context."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTEXT_DIR = PROJECT_ROOT / "issues" / "context"
PLANS_DIR = PROJECT_ROOT / "issues" / "plans"


BUCKET_KEYS = [
    "cover_feature",
    "music_features",
    "chart_watch",
    "albums_and_artists",
    "screen_tv_film",
    "cultural_snapshot",
    "sidebars_fast_facts",
    "visual_concepts",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate year-level editorial planning outputs.")
    parser.add_argument("--year", type=int, required=True, help="Issue year to plan.")
    return parser.parse_args()


def as_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def read_context(year: int) -> dict[str, Any]:
    path = CONTEXT_DIR / f"{year}_context.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing context file: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Context file root is not an object: {path}")
    return payload


def first_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return rows[0] if rows else {}


def song_label(row: dict[str, Any]) -> str:
    title = str(row.get("title", "")).strip()
    artist = str(row.get("artist", "")).strip()
    if title and artist:
        return f"{title} — {artist}"
    return title or artist or "No data"


def album_label(row: dict[str, Any]) -> str:
    album = str(row.get("album", row.get("title", ""))).strip()
    artist = str(row.get("artist", "")).strip()
    if album and artist:
        return f"{album} — {artist}"
    return album or artist or "No data"


def safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def gather_signals(year: int, context: dict[str, Any]) -> dict[str, Any]:
    top_songs = safe_list(context.get("top_songs"))
    top_artists = safe_list(context.get("top_artists"))
    top_albums = safe_list(context.get("albums", {}).get("top_albums")) if isinstance(context.get("albums"), dict) else []
    dominant_album_artists = (
        safe_list(context.get("albums", {}).get("dominant_artists")) if isinstance(context.get("albums"), dict) else []
    )
    power_index = safe_list(context.get("artist_power_index"))
    chart_dynamics = context.get("chart_dynamics", {}) if isinstance(context.get("chart_dynamics"), dict) else {}
    album_dynamics = context.get("album_dynamics", {}) if isinstance(context.get("album_dynamics"), dict) else {}
    sonic = context.get("sonic_profile", {}) if isinstance(context.get("sonic_profile"), dict) else {}
    movies = safe_list(context.get("movies"))
    television = safe_list(context.get("television"))
    cultural_events = safe_list(context.get("cultural_events"))

    soundtrack_count = sum(
        1
        for row in top_albums
        if "soundtrack" in str(row.get("artist", "")).lower() or "soundtrack" in str(row.get("album", "")).lower()
    )
    danceability = as_float(sonic.get("average_danceability")) or 0.0
    energy = as_float(sonic.get("average_energy")) or 0.0
    valence = as_float(sonic.get("average_valence")) or 0.0
    danceable_percent = as_int(sonic.get("danceable_tracks_percent")) or 0
    dominant_mood = str(sonic.get("dominant_mood", "")).strip().lower()
    top_power_artist = first_row(power_index)
    fastest_riser = first_row(safe_list(chart_dynamics.get("fastest_risers")))
    longest_album_no1 = first_row(safe_list(album_dynamics.get("longest_number_one_runs")))
    longest_top10_song = first_row(safe_list(chart_dynamics.get("longest_top10_runs")))

    return {
        "year": year,
        "top_songs": top_songs,
        "top_artists": top_artists,
        "top_albums": top_albums,
        "dominant_album_artists": dominant_album_artists,
        "power_index": power_index,
        "chart_dynamics": chart_dynamics,
        "album_dynamics": album_dynamics,
        "sonic": sonic,
        "movies": movies,
        "television": television,
        "cultural_events": cultural_events,
        "soundtrack_count": soundtrack_count,
        "danceability": danceability,
        "energy": energy,
        "valence": valence,
        "danceable_percent": danceable_percent,
        "dominant_mood": dominant_mood,
        "top_power_artist": top_power_artist,
        "fastest_riser": fastest_riser,
        "longest_album_no1": longest_album_no1,
        "longest_top10_song": longest_top10_song,
    }


def derive_year_identity(signals: dict[str, Any]) -> dict[str, Any]:
    soundtrack_count = int(signals["soundtrack_count"])
    dance_pct = int(signals["danceable_percent"])
    danceability = float(signals["danceability"])
    energy = float(signals["energy"])
    valence = float(signals["valence"])
    mood = str(signals["dominant_mood"])

    if soundtrack_count >= 2:
        primary_music_story = "Crossover soundtrack culture pushed songs and albums into the same mainstream spotlight"
    elif dance_pct >= 45 or danceability >= 0.58:
        primary_music_story = "Dancefloor-oriented singles drove the year’s pop momentum"
    elif energy >= 0.62:
        primary_music_story = "High-energy chart turnover defined the year’s radio conversation"
    else:
        primary_music_story = "Mainstream pop moved through multiple styles while maintaining strong weekly chart churn"

    top_album = album_label(first_row(signals["top_albums"]))
    top_artist = str(first_row(signals["power_index"]).get("artist", "")).strip()
    if top_artist:
        secondary_music_story = (
            f"Artist-level staying power remained strong, with {top_artist} and other repeat names anchoring the year"
        )
    elif top_album != "No data":
        secondary_music_story = f"Album-era loyalty remained visible through long-running releases like {top_album}"
    else:
        secondary_music_story = "Albums retained narrative weight alongside fast-moving singles charts"

    if mood == "upbeat":
        sonic_character = "Bright, dance-forward, and momentum-heavy with a glossy mainstream edge"
    elif mood == "intense":
        sonic_character = "High-energy and urgent, with forceful chart movement and sharp peaks"
    elif mood == "mellow":
        sonic_character = "Warm, reflective, and low-friction, with slower sonic pacing"
    else:
        if valence >= 0.55 and energy >= 0.5:
            sonic_character = "Upbeat and groove-led, balancing polish with movement"
        elif energy < 0.45:
            sonic_character = "Measured and atmospheric, with a softer rhythmic footprint"
        else:
            sonic_character = "Balanced and kinetic, mixing dance cues with broad pop accessibility"

    lead_song = song_label(first_row(signals["top_songs"]))
    editorial_angle = (
        f"{signals['year']} reads as a year of cultural motion: weekly chart volatility, durable album stories, "
        f"and headline tracks such as {lead_song} acting as connective tissue."
    )

    return {
        "primary_music_story": primary_music_story,
        "secondary_music_story": secondary_music_story,
        "sonic_character": sonic_character,
        "editorial_angle": editorial_angle,
    }


def toc_item(title: str, format_name: str, source_basis: list[str]) -> dict[str, Any]:
    return {"title": title, "format": format_name, "source_basis": source_basis}


def build_table_of_contents(signals: dict[str, Any], identity: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    fastest_riser = song_label(first_row(safe_list(signals["chart_dynamics"].get("fastest_risers"))))
    longest_album_run = album_label(first_row(safe_list(signals["album_dynamics"].get("longest_number_one_runs"))))
    top_movie = str(first_row(signals["movies"])) if signals["movies"] else "Top theatrical release"
    top_tv = str(first_row(signals["television"])) if signals["television"] else "Prime-time benchmark series"

    return {
        "cover_feature": [
            toc_item(identity["primary_music_story"], "feature", ["top_songs", "artist_power_index", "sonic_profile"]),
            toc_item("The Year in One Data Narrative", "visual explainer", ["chart_dynamics", "album_dynamics", "context_sources"]),
        ],
        "music_features": [
            toc_item("How the Top 10 Sounded Week to Week", "chart breakdown", ["top_songs", "sonic_profile"]),
            toc_item("Artists Who Controlled the Year", "profile", ["artist_power_index", "top_artists"]),
            toc_item(f"Breakout Momentum: {fastest_riser}", "short narrative", ["chart_dynamics.fastest_risers"]),
        ],
        "chart_watch": [
            toc_item("Fastest Risers and Fastest Fallers", "chart breakdown", ["chart_dynamics.fastest_risers", "chart_dynamics.fastest_fallers"]),
            toc_item("The Long Run: Top 10 and Full-Chart Endurance", "timeline", ["chart_dynamics.longest_top10_runs", "chart_dynamics.longest_chart_runs"]),
            toc_item("The #2 Ceiling and Near-Miss Zone", "list", ["chart_dynamics.longest_number_two_streaks", "chart_dynamics.near_miss_hits"]),
        ],
        "albums_and_artists": [
            toc_item("Album Dominance Map", "chart breakdown", ["albums.top_albums", "album_dynamics.longest_number_one_runs"]),
            toc_item(f"Longest Album Reign: {longest_album_run}", "short narrative", ["album_dynamics.longest_number_one_runs"]),
            toc_item("Slow Climbs to #1", "timeline", ["album_dynamics.slowest_climb_to_number_one"]),
        ],
        "screen_tv_film": [
            toc_item(f"Film Pulse: {top_movie} and the Year’s Screen Mood", "list", ["movies", "cultural_events"]),
            toc_item(f"Television Baseline: {top_tv}", "short narrative", ["television"]),
        ],
        "cultural_snapshot": [
            toc_item("Ten Headlines That Framed the Year", "timeline", ["cultural_events"]),
            toc_item("Mainstream Attention Economy: Music, Film, TV", "visual explainer", ["top_songs", "movies", "television"]),
        ],
        "sidebars_fast_facts": [
            toc_item("Eight Chart Highlight Callouts", "sidebar", ["chart_dynamics", "album_dynamics"]),
            toc_item("Sonic Fingerprint Card", "data card set", ["sonic_profile", "sonic_extremes"]),
            toc_item("If You Only Know Three Tracks", "list", ["top_songs", "artist_power_index"]),
        ],
        "visual_concepts": [
            toc_item("Disco Floor Momentum Spread", "visual explainer", ["year_identity", "sonic_profile"]),
            toc_item("Chart Volatility Grids", "data card set", ["chart_dynamics"]),
            toc_item("Album Reign Timeline", "data card set", ["album_dynamics"]),
        ],
    }


def assignment(
    idx: int,
    title: str,
    category: str,
    format_name: str,
    rationale: str,
    source_basis: list[str],
    priority: str,
    estimated_length: str,
    reusable_for: list[str],
) -> dict[str, Any]:
    return {
        "id": f"story_{idx:03d}",
        "title": title,
        "category": category,
        "format": format_name,
        "rationale": rationale,
        "source_basis": source_basis,
        "priority": priority,
        "estimated_length": estimated_length,
        "reusable_for": reusable_for,
    }


def build_story_assignments(signals: dict[str, Any], identity: dict[str, Any]) -> list[dict[str, Any]]:
    top_song = song_label(first_row(signals["top_songs"]))
    fastest_riser = song_label(first_row(safe_list(signals["chart_dynamics"].get("fastest_risers"))))
    biggest_faller = song_label(first_row(safe_list(signals["chart_dynamics"].get("fastest_fallers"))))
    near_miss = song_label(first_row(safe_list(signals["chart_dynamics"].get("near_miss_hits"))))
    top_album = album_label(first_row(signals["top_albums"]))
    top_album_run = album_label(first_row(safe_list(signals["album_dynamics"].get("longest_number_one_runs"))))
    slow_album = album_label(first_row(safe_list(signals["album_dynamics"].get("slowest_climb_to_number_one"))))
    top_power_artist = str(first_row(signals["power_index"]).get("artist", "Top ranking artist")).strip() or "Top ranking artist"
    movie = str(first_row(signals["movies"])) if signals["movies"] else "Top film title"
    show = str(first_row(signals["television"])) if signals["television"] else "Top television title"

    assignments = [
        assignment(
            1,
            identity["primary_music_story"],
            "cover_feature",
            "feature",
            "The primary narrative is directly supported by chart leadership, artist concentration, and sonic profile signals.",
            ["top_songs", "artist_power_index", "sonic_profile", "chart_dynamics.longest_top10_runs"],
            "high",
            "long",
            ["magazine", "slideshow", "live event script"],
        ),
        assignment(
            2,
            f"{top_power_artist}: The Year’s Power Curve",
            "music_features",
            "profile",
            "Artist Power Index and repeat chart placement identify this as a high-leverage profile for the issue spine.",
            ["artist_power_index", "top_artists", "chart_dynamics.longest_chart_runs"],
            "high",
            "medium",
            ["magazine", "social", "timeline cards"],
        ),
        assignment(
            3,
            f"From Debut to Top 10: {top_song}",
            "music_features",
            "short narrative",
            "A representative lead track provides a concrete path through weekly momentum and mainstream reception.",
            ["top_songs", "chart_dynamics.slow_burn_hits", "chart_dynamics.longest_top10_runs"],
            "high",
            "medium",
            ["magazine", "trivia", "social"],
        ),
        assignment(
            4,
            f"Fastest Climb of the Year: {fastest_riser}",
            "chart_watch",
            "chart breakdown",
            "Largest single-week rise offers a clean data-first chart movement story.",
            ["chart_dynamics.fastest_risers", "chart_dynamics.largest_single_week_jump"],
            "high",
            "short",
            ["magazine", "timeline cards", "slideshow"],
        ),
        assignment(
            5,
            f"Sharpest Drop on the Board: {biggest_faller}",
            "chart_watch",
            "chart breakdown",
            "Largest week-over-week decline adds contrast and helps explain volatility in the same cycle.",
            ["chart_dynamics.fastest_fallers", "chart_dynamics.largest_single_week_drop"],
            "medium",
            "short",
            ["magazine", "trivia", "social"],
        ),
        assignment(
            6,
            f"Album Gravity: {top_album_run}",
            "albums_and_artists",
            "feature",
            "Album-level duration and number-one persistence justify a dedicated long-form album dominance piece.",
            ["albums.top_albums", "album_dynamics.longest_number_one_runs", "albums.dominant_artists"],
            "high",
            "long",
            ["magazine", "slideshow", "live event script"],
        ),
        assignment(
            7,
            f"Slow Climb, Big Payoff: {slow_album}",
            "albums_and_artists",
            "timeline",
            "Weeks-to-#1 pattern reveals long-arc adoption behavior that differs from singles velocity.",
            ["album_dynamics.slowest_climb_to_number_one", "albums.top_albums"],
            "medium",
            "medium",
            ["magazine", "timeline cards", "social"],
        ),
        assignment(
            8,
            f"Screen-Year Pulse: {movie}",
            "screen_tv_film",
            "list",
            "Film list plus event timeline supports a concise screen-culture readout tied to the same year context.",
            ["movies", "cultural_events"],
            "medium",
            "short",
            ["magazine", "social", "slideshow"],
        ),
        assignment(
            9,
            f"Television in the Room: {show}",
            "screen_tv_film",
            "short narrative",
            "TV rankings anchor a practical companion piece to the film spread.",
            ["television", "cultural_events"],
            "medium",
            "short",
            ["magazine", "social"],
        ),
        assignment(
            10,
            "The Week-by-Week Yearline",
            "cultural_snapshot",
            "timeline",
            "A compact chronology maps headlines, chart turns, and screen signals into one shared frame.",
            ["cultural_events", "chart_dynamics", "album_dynamics"],
            "high",
            "medium",
            ["magazine", "timeline cards", "live event script"],
        ),
        assignment(
            11,
            f"Almost Hits: {near_miss}",
            "sidebars_fast_facts",
            "sidebar",
            "Near-miss records are highly reusable and work well as quick-reference editorial modules.",
            ["chart_dynamics.near_miss_hits"],
            "medium",
            "short",
            ["magazine", "trivia", "bingo", "social"],
        ),
        assignment(
            12,
            "Sonic Fingerprint Card Set",
            "sidebars_fast_facts",
            "data card set",
            "Audio-feature aggregates and extremes produce durable sidebars for print and digital reuse.",
            ["sonic_profile", "sonic_extremes", "context_sources"],
            "high",
            "short",
            ["magazine", "social", "timeline cards", "slideshow"],
        ),
    ]
    return assignments


def highlight_item(label: str, subject: str, summary: str, source_basis: str) -> dict[str, Any]:
    return {"label": label, "subject": subject, "short_summary": summary, "source_basis": source_basis}


def build_chart_highlights(signals: dict[str, Any]) -> list[dict[str, Any]]:
    chart = signals["chart_dynamics"]
    album = signals["album_dynamics"]

    fastest_riser = first_row(safe_list(chart.get("fastest_risers")))
    fastest_faller = first_row(safe_list(chart.get("fastest_fallers")))
    longest_top10 = first_row(safe_list(chart.get("longest_top10_runs")))
    longest_chart = first_row(safe_list(chart.get("longest_chart_runs")))
    longest_two = first_row(safe_list(chart.get("longest_number_two_streaks")))
    near_miss = first_row(safe_list(chart.get("near_miss_hits")))
    album_no1 = first_row(safe_list(album.get("longest_number_one_runs")))
    slow_album = first_row(safe_list(album.get("slowest_climb_to_number_one")))

    return [
        highlight_item(
            "Fastest Climber",
            song_label(fastest_riser),
            "Made the sharpest upward weekly move on the Hot 100 in the target year.",
            "chart_dynamics.fastest_risers",
        ),
        highlight_item(
            "Biggest Faller",
            song_label(fastest_faller),
            "Posted the steepest single-week drop among charted songs.",
            "chart_dynamics.fastest_fallers",
        ),
        highlight_item(
            "Longest Top 10 Run",
            song_label(longest_top10),
            "Stayed in the Top 10 longer than any other song in the year snapshot.",
            "chart_dynamics.longest_top10_runs",
        ),
        highlight_item(
            "Longest Chart Run",
            song_label(longest_chart),
            "Logged the longest overall Hot 100 run for the year.",
            "chart_dynamics.longest_chart_runs",
        ),
        highlight_item(
            "Longest #2 Song",
            song_label(longest_two),
            "Spent the most time at rank #2 without owning the #1 slot for that stretch.",
            "chart_dynamics.longest_number_two_streaks",
        ),
        highlight_item(
            "Strongest Near-Miss Hit",
            song_label(near_miss),
            "Peaked in the 41-45 zone while never officially entering the Top 40.",
            "chart_dynamics.near_miss_hits",
        ),
        highlight_item(
            "Longest #1 Album Run",
            album_label(album_no1),
            "Held the top album position longer than any competing release that year.",
            "album_dynamics.longest_number_one_runs",
        ),
        highlight_item(
            "Slowest Climb to #1 Album",
            album_label(slow_album),
            "Took the longest runway to reach the #1 album position.",
            "album_dynamics.slowest_climb_to_number_one",
        ),
    ]


def snapshot_box(title: str, box_type: str, summary: str, sources: list[str]) -> dict[str, Any]:
    return {"title": title, "type": box_type, "summary": summary, "supporting_sources": sources}


def build_year_snapshot_boxes(signals: dict[str, Any], identity: dict[str, Any]) -> list[dict[str, Any]]:
    top_three_songs = [song_label(row) for row in signals["top_songs"][:3]]
    top_three_albums = [album_label(row) for row in signals["top_albums"][:3]]
    top_three_movies = [str(item) for item in signals["movies"][:3]]
    top_three_tv = [str(item) for item in signals["television"][:3]]
    near_miss = safe_list(signals["chart_dynamics"].get("near_miss_hits"))[:3]
    near_miss_labels = [song_label(row) for row in near_miss]

    sonic = signals["sonic"]
    sonic_line = (
        f"Avg danceability {sonic.get('average_danceability', 0)}, "
        f"energy {sonic.get('average_energy', 0)}, "
        f"valence {sonic.get('average_valence', 0)}; "
        f"{sonic.get('danceable_tracks_percent', 0)}% of tracks clear the danceable threshold."
    )

    boxes = [
        snapshot_box(
            "If You Only Knew 3 Songs",
            "quick picks",
            "; ".join(top_three_songs) if top_three_songs else "Song shortlist unavailable in current context.",
            ["top_songs", "artist_power_index"],
        ),
        snapshot_box(
            "Albums That Defined the Room",
            "album stack",
            "; ".join(top_three_albums) if top_three_albums else "Album shortlist unavailable in current context.",
            ["albums.top_albums", "album_dynamics.longest_number_one_runs"],
        ),
        snapshot_box(
            "The Sound of the Year",
            "sonic profile",
            sonic_line,
            ["sonic_profile", "sonic_extremes"],
        ),
        snapshot_box(
            "Hits That Almost Broke Through",
            "near miss",
            "; ".join(near_miss_labels) if near_miss_labels else "No near-miss samples detected in current chart dynamics.",
            ["chart_dynamics.near_miss_hits"],
        ),
        snapshot_box(
            "Movies Everyone Was Talking About",
            "screen pulse",
            "; ".join(top_three_movies) if top_three_movies else "Movie shortlist unavailable in current context.",
            ["movies", "cultural_events"],
        ),
        snapshot_box(
            "TV in the Background of America",
            "broadcast baseline",
            "; ".join(top_three_tv) if top_three_tv else "TV shortlist unavailable in current context.",
            ["television"],
        ),
        snapshot_box(
            "Power Artist Snapshot",
            "data card",
            f"{str(first_row(signals['power_index']).get('artist', 'Top-ranked artist'))} leads the blended singles/album score model.",
            ["artist_power_index"],
        ),
        snapshot_box(
            "Editorial Angle in One Line",
            "angle",
            identity["editorial_angle"],
            ["year_identity", "context_sources", "chart_dynamics", "album_dynamics"],
        ),
    ]
    return boxes


def visual_concept(
    concept_name: str,
    intended_story: str,
    visual_theme: str,
    key_objects: list[str],
    mood: str,
) -> dict[str, Any]:
    return {
        "concept_name": concept_name,
        "intended_story": intended_story,
        "visual_theme": visual_theme,
        "key_objects": key_objects,
        "mood": mood,
        "dependency": "article must be written first",
    }


def build_visual_concepts(assignments: list[dict[str, Any]], identity: dict[str, Any]) -> list[dict[str, Any]]:
    cover_story = assignments[0]["title"] if assignments else identity["primary_music_story"]
    return [
        visual_concept(
            "Momentum City Night",
            cover_story,
            "Neon nightlife + dense crowd motion + reflective textures",
            ["dance floor lights", "record sleeves", "street marquees", "radio dial"],
            "kinetic / social / bright",
        ),
        visual_concept(
            "Chart Velocity Grid",
            "Fastest Climb of the Year",
            "Weekly rank movement as slanted arrow fields and heat bands",
            ["rank arrows", "week labels", "peak markers", "jump callouts"],
            "analytic / high-contrast / fast",
        ),
        visual_concept(
            "Album Reign Corridor",
            "Album Gravity feature",
            "Long hallway of stacked album spines and #1 checkpoints",
            ["album spines", "calendar strip", "number-one badges", "artist silhouettes"],
            "steady / monumental / archival",
        ),
        visual_concept(
            "Near-Miss Bulletin Board",
            "Almost Hits sidebar",
            "Pinned index cards for songs that nearly entered Top 40",
            ["bulletin pins", "rank tags", "mini charts", "annotated notes"],
            "curious / playful / investigative",
        ),
        visual_concept(
            "Sonic Fingerprint Dashboard",
            "Sonic Fingerprint Card Set",
            "Analog-meets-data panel with dials for danceability, energy, valence",
            ["VU meters", "tempo arc", "mood gauge", "track callouts"],
            "technical / tactile / editorial",
        ),
        visual_concept(
            "Screen and Living Room Split",
            "Screen-Year Pulse + Television Baseline",
            "Cinema marquee and living room TV as mirrored halves",
            ["movie marquee", "remote control", "sofa silhouette", "ticket stubs"],
            "domestic / cinematic / period-aware",
        ),
    ]


def build_plan(year: int, context: dict[str, Any]) -> dict[str, Any]:
    signals = gather_signals(year, context)
    identity = derive_year_identity(signals)
    toc = build_table_of_contents(signals, identity)
    assignments = build_story_assignments(signals, identity)
    highlights = build_chart_highlights(signals)
    snapshot_boxes = build_year_snapshot_boxes(signals, identity)
    visuals = build_visual_concepts(assignments, identity)

    return {
        "year": year,
        "year_identity": identity,
        "table_of_contents": toc,
        "story_assignments": assignments,
        "chart_highlights": highlights,
        "year_snapshot_boxes": snapshot_boxes,
        "visual_concepts": visuals,
    }


def markdown_section_header(title: str) -> str:
    return f"## {title}\n"


def render_markdown(plan: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# RetroVerse Narrative Plan {plan['year']}")
    lines.append("")

    identity = plan["year_identity"]
    lines.append(markdown_section_header("Year Identity").rstrip())
    lines.append(f"- Primary music story: {identity['primary_music_story']}")
    lines.append(f"- Secondary music story: {identity['secondary_music_story']}")
    lines.append(f"- Sonic character: {identity['sonic_character']}")
    lines.append(f"- Editorial angle: {identity['editorial_angle']}")
    lines.append("")

    lines.append(markdown_section_header("Proposed Table Of Contents").rstrip())
    toc: dict[str, list[dict[str, Any]]] = plan["table_of_contents"]
    bucket_labels = {
        "cover_feature": "Cover Feature",
        "music_features": "Music Features",
        "chart_watch": "Chart Watch",
        "albums_and_artists": "Albums & Artists",
        "screen_tv_film": "Screen / TV / Film",
        "cultural_snapshot": "Cultural Snapshot",
        "sidebars_fast_facts": "Sidebars / Fast Facts",
        "visual_concepts": "Visual Concepts",
    }
    for key in BUCKET_KEYS:
        lines.append(f"### {bucket_labels[key]}")
        for item in toc.get(key, []):
            lines.append(f"- {item['title']} ({item['format']})")
            lines.append(f"  Source basis: {', '.join(item.get('source_basis', []))}")
        lines.append("")

    lines.append(markdown_section_header("Story Assignments").rstrip())
    for item in plan["story_assignments"]:
        lines.append(f"### {item['id']}: {item['title']}")
        lines.append(f"- Category: {item['category']}")
        lines.append(f"- Format: {item['format']}")
        lines.append(f"- Priority: {item['priority']}")
        lines.append(f"- Estimated length: {item['estimated_length']}")
        lines.append(f"- Rationale: {item['rationale']}")
        lines.append(f"- Source basis: {', '.join(item.get('source_basis', []))}")
        lines.append(f"- Reusable for: {', '.join(item.get('reusable_for', []))}")
        lines.append("")

    lines.append(markdown_section_header("Chart Highlights").rstrip())
    for item in plan["chart_highlights"]:
        lines.append(f"- {item['label']}: {item['subject']}")
        lines.append(f"  {item['short_summary']} ({item['source_basis']})")
    lines.append("")

    lines.append(markdown_section_header("Year Snapshot Boxes").rstrip())
    for item in plan["year_snapshot_boxes"]:
        lines.append(f"- {item['title']} [{item['type']}]")
        lines.append(f"  {item['summary']}")
        lines.append(f"  Supporting sources: {', '.join(item.get('supporting_sources', []))}")
    lines.append("")

    lines.append(markdown_section_header("Visual Concepts").rstrip())
    for item in plan["visual_concepts"]:
        lines.append(f"### {item['concept_name']}")
        lines.append(f"- Intended story: {item['intended_story']}")
        lines.append(f"- Visual theme: {item['visual_theme']}")
        lines.append(f"- Key objects: {', '.join(item.get('key_objects', []))}")
        lines.append(f"- Mood: {item['mood']}")
        lines.append(f"- Dependency: {item['dependency']}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def validate_plan(plan: dict[str, Any]) -> None:
    required_keys = {
        "year_identity",
        "table_of_contents",
        "story_assignments",
        "chart_highlights",
        "year_snapshot_boxes",
        "visual_concepts",
    }
    missing = [key for key in required_keys if key not in plan]
    if missing:
        raise ValueError(f"Narrative plan missing required keys: {', '.join(sorted(missing))}")
    if not isinstance(plan["story_assignments"], list) or not (10 <= len(plan["story_assignments"]) <= 18):
        raise ValueError("story_assignments must contain between 10 and 18 items.")


def main() -> int:
    args = parse_args()
    year = int(args.year)

    context = read_context(year)
    plan = build_plan(year, context)
    validate_plan(plan)

    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = PLANS_DIR / f"{year}_narrative_plan.json"
    md_path = PLANS_DIR / f"{year}_narrative_plan.md"

    json_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(plan), encoding="utf-8")

    print(f"Wrote narrative plan JSON: {json_path}")
    print(f"Wrote narrative plan Markdown: {md_path}")
    print(f"Story assignments: {len(plan['story_assignments'])}")
    print(f"Snapshot boxes: {len(plan['year_snapshot_boxes'])}")
    print(f"Visual concepts: {len(plan['visual_concepts'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
