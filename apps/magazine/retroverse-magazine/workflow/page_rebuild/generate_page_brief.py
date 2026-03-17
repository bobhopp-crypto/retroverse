#!/usr/bin/env python3
"""Generate a structured page brief for the controlled single-page rebuild."""

from __future__ import annotations

from common import DEFAULT_TEXT_SAFE_ZONES
from common import PAGE_DIMENSIONS
from common import build_parser
from common import clean_text
from common import find_song_entry
from common import load_page_bundle
from common import output_path
from common import write_json


def main() -> None:
    parser = build_parser("Generate the single-page rebuild brief.")
    args = parser.parse_args()

    bundle = load_page_bundle(args.year, args.page_slug)
    target = bundle["target"]
    final_story = bundle["final_story"]
    movies_data = bundle["movies_data"]
    context = bundle["context"]
    production_target = bundle["production_target"] or {}
    narrative_story = bundle["narrative_story"] or {}
    story_design = bundle["story_design"] or {}
    visual_brief = bundle["visual_brief"] or {}

    top_songs = context.get("top_songs", [])
    grease_song = find_song_entry(top_songs, "Grease")
    you_re_the_one = find_song_entry(top_songs, "You're The One That I Want")

    top_films = movies_data.get("films", [])
    page_title = f"{args.year} Movies of the Year"
    page_subtitle = final_story.get("headline", "Screen-Year Pulse: Grease")

    writer = {
        "name": final_story.get("writer", "Lola Vance"),
        "role": "Film & Television Critic",
        "byline": final_story.get("byline", "By Lola Vance"),
        "authority_note": (
            "This controlled rebuild uses the mapped final story asset "
            f"`{target.story_id}` as the text authority. The legacy canonical page credits "
            f"{bundle['canonical_byline'] or 'a placeholder byline'}, but the rebuild follows the "
            "story-first production target where final prose exists before art direction."
        ),
    }

    page_purpose = (
        "Rebuild page 16 as a single portrait editorial movie feature that uses the finalized "
        f"`{page_subtitle}` story as the primary text layer, grounds the page in verified 1978 movie "
        "rankings and soundtrack crossover facts, and reserves clean overlay zones so illustration "
        "can remain text-free until layout."
    )

    story_summary = (
        "The page treats Grease as the clearest symbol of 1978 moviegoing momentum while framing the "
        "year's screen mood as a broader pattern of repeat audience attention. Superman and Animal House "
        "support that larger picture, and the soundtrack crossover facts from the legacy page explain "
        "why movie culture kept echoing back through radio and everyday conversation. Final title, body "
        "copy, sidebar facts, and page number will be overlaid after illustration delivery."
    )

    verified_facts = [
        {
            "claim": "The 1978 movie dataset contains ten ranked film entries for the page.",
            "source_file": "issues/1978/data/movies.json",
            "evidence": f"{len(top_films)} ranked films are present in the `films` array.",
            "kind": "dataset_inventory",
        },
        {
            "claim": "Grease is ranked #1 in the 1978 movie dataset.",
            "source_file": "issues/1978/data/movies.json",
            "evidence": top_films[0]["note"],
            "kind": "movie_rank",
        },
        {
            "claim": "Superman is ranked #2 in the 1978 movie dataset.",
            "source_file": "issues/1978/data/movies.json",
            "evidence": top_films[1]["note"],
            "kind": "movie_rank",
        },
        {
            "claim": "Animal House is ranked #3 in the 1978 movie dataset.",
            "source_file": "issues/1978/data/movies.json",
            "evidence": top_films[2]["note"],
            "kind": "movie_rank",
        },
        {
            "claim": "The production target for the movies page requires final prose before art.",
            "source_file": "issues/1978/layout/1978_production_targets.json",
            "evidence": (
                f"`{target.story_id}` is marked `illustration_required: true` and "
                "`final_prose_required_before_art: true`."
            ),
            "kind": "process_guardrail",
        },
    ]

    if you_re_the_one:
        verified_facts.append(
            {
                "claim": "\"You're The One That I Want\" is a verified soundtrack crossover signal in the 1978 context data.",
                "source_file": "issues/context/1978_context.json",
                "evidence": (
                    f"Rank {you_re_the_one['rank']}, {you_re_the_one['weeks']} weeks, "
                    f"peak #{you_re_the_one['peak']}, score {you_re_the_one['score']}."
                ),
                "kind": "soundtrack_crossover",
            }
        )
    if grease_song:
        verified_facts.append(
            {
                "claim": "\"Grease\" by Frankie Valli is another verified soundtrack crossover signal in the 1978 context data.",
                "source_file": "issues/context/1978_context.json",
                "evidence": (
                    f"Rank {grease_song['rank']}, {grease_song['weeks']} weeks, "
                    f"peak #{grease_song['peak']}, score {grease_song['score']}."
                ),
                "kind": "soundtrack_crossover",
            }
        )

    text_blocks = [
        {
            "id": "page_title",
            "role": "title",
            "label": "Page title",
            "content": page_title,
            "source_file": "issues/1978/movies.md",
            "intended_zone": "title_zone",
        },
        {
            "id": "page_subtitle",
            "role": "subtitle",
            "label": "Story subtitle",
            "content": page_subtitle,
            "source_file": "issues/1978/articles/final/story_008.json",
            "intended_zone": "title_zone",
        },
        {
            "id": "page_byline",
            "role": "byline",
            "label": "Byline",
            "content": writer["byline"],
            "source_file": "issues/1978/articles/final/story_008.json",
            "intended_zone": "title_zone",
        },
        {
            "id": "page_deck",
            "role": "deck",
            "label": "Deck",
            "content": (
                "A critic's screen-year read on how Grease, Superman, and Animal House concentrated "
                "1978 moviegoing energy while soundtrack crossover kept the page tied to the rest of the issue."
            ),
            "source_file": "issues/plans/1978_narrative_plan.json",
            "intended_zone": "title_zone",
        },
        {
            "id": "body_lede",
            "role": "body",
            "label": "Body paragraph 1",
            "content": clean_text(final_story["sections"]["lede"]),
            "source_file": "issues/1978/articles/final/story_008.json",
            "intended_zone": "body_zone",
        },
        {
            "id": "body_analysis",
            "role": "body",
            "label": "Body paragraph 2",
            "content": clean_text(final_story["sections"]["analysis"]),
            "source_file": "issues/1978/articles/final/story_008.json",
            "intended_zone": "body_zone",
        },
        {
            "id": "body_significance",
            "role": "body",
            "label": "Body paragraph 3",
            "content": clean_text(final_story["sections"]["cultural_significance"]),
            "source_file": "issues/1978/articles/final/story_008.json",
            "intended_zone": "body_zone",
        },
        {
            "id": "body_closing",
            "role": "body",
            "label": "Body paragraph 4",
            "content": clean_text(final_story["sections"]["closing"]),
            "source_file": "issues/1978/articles/final/story_008.json",
            "intended_zone": "body_zone",
        },
    ]

    sidebar_blocks = [
        {
            "id": "movie_leaders",
            "title": "1978 Movie Leaders",
            "intended_zone": "sidebar_zone",
            "items": [
                {
                    "label": f"#{film['rank']} {film['title']}",
                    "value": film["note"],
                    "source_file": "issues/1978/data/movies.json",
                }
                for film in top_films[:3]
            ],
        }
    ]

    soundtrack_items = []
    if you_re_the_one:
        soundtrack_items.append(
            {
                "label": "\"You're The One That I Want\"",
                "value": f"{you_re_the_one['weeks']} weeks, peak #{you_re_the_one['peak']}, score {you_re_the_one['score']}",
                "source_file": "issues/context/1978_context.json",
            }
        )
    if grease_song:
        soundtrack_items.append(
            {
                "label": "\"Grease\"",
                "value": f"{grease_song['weeks']} weeks, peak #{grease_song['peak']}, score {grease_song['score']}",
                "source_file": "issues/context/1978_context.json",
            }
        )
    if soundtrack_items:
        sidebar_blocks.append(
            {
                "id": "soundtrack_crossover",
                "title": "Soundtrack Crossover",
                "intended_zone": "sidebar_zone",
                "items": soundtrack_items,
            }
        )

    qa_notes = [
        "Final story asset exists before art direction and is treated as the authoritative text layer for the rebuild.",
        (
            "Legacy page copy in `issues/1978/movies.md` is retained as source context only; the controlled rebuild "
            "uses the mapped story_008 package because the issue map places the movies page in the feature well."
        ),
        "Text-safe zones are normalized to a 900x1200 portrait page and must remain open during illustration.",
        "Artwork must be delivered as page-aware background art with no production headline, body, or stat typography baked in.",
    ]

    layout_requirements = {
        "page_number": target.page_number,
        "orientation": "portrait",
        "page_dimensions": PAGE_DIMENSIONS,
        "structure": (
            "Full-page background illustration with a calm upper-left title block, a two-column body region "
            "across the lower-left and center, a compact right-rail sidebar/stat box, and a small footer page number."
        ),
        "overlay_order": [
            "background/page art first",
            "title, subtitle, byline, and deck",
            "body text",
            "sidebar/stat box",
            "page number",
        ],
        "art_placement": {
            "mode": "full-page background with right-heavy focal scene",
            "focal_scene_note": (
                "Concentrate marquee, crowd, and strongest contrast on the upper/right half so the title and body zones stay readable."
            ),
            "final_art_inserted_later": True,
        },
    }

    art_direction = {
        "page_readback": (
            "Read this as a whole page, not a spot illustration: page 16 is a single-page movie feature whose text is already written "
            "and whose art must support the Grease-led 1978 screen mood without taking over the title/body/sidebar zones."
        ),
        "concept": (
            "Build a rainy 1978 theater-district editorial scene with a marquee glow, queueing moviegoers, ticket-booth details, and "
            "supporting hints of Grease, Superman, and Animal House, while holding the left half and lower text fields open."
        ),
        "focus_objects": [
            "theater marquee glow",
            "moviegoer crowd line",
            "ticket booth or ticket stub detail",
            "wet sidewalk reflections",
            "poster cases or film-reel ephemera kept secondary",
        ],
        "negative_space_strategy": (
            "Keep the title zone bright and low-clutter, keep the two-column body zone mostly low-contrast, "
            "and avoid bright bulbs, faces, or hard edges in the sidebar and footer zones."
        ),
        "text_rendering_rule": "Illustration supplies image and atmosphere only. Final production text is overlaid later by layout.",
    }

    brief = {
        "year": args.year,
        "page_type": target.page_type,
        "page_slug": args.page_slug,
        "title": page_title,
        "subtitle": page_subtitle,
        "writer": writer,
        "source_files": bundle["source_files"],
        "page_purpose": page_purpose,
        "story_summary": story_summary,
        "verified_facts": verified_facts,
        "text_blocks": text_blocks,
        "sidebar_blocks": sidebar_blocks,
        "qa_notes": qa_notes,
        "layout_requirements": layout_requirements,
        "art_direction": art_direction,
        "text_safe_zones": DEFAULT_TEXT_SAFE_ZONES,
        "must_include": [
            page_title,
            page_subtitle,
            writer["byline"],
            "Final body copy sourced from `issues/1978/articles/final/story_008.json`",
            "Verified movie ranking sidebar/stat box",
            "Page number 16",
            "Full-page page-aware illustration background inserted later",
        ],
        "must_not_render_in_art": [
            "article body text",
            "charts/tables",
            "exact production typography",
            "page title and subtitle",
            "byline text",
            "sidebar labels and stat text",
            "page number",
        ],
        "style_notes": [
            "Late-1970s editorial print look with analog grain and restrained halftone texture.",
            "Cinematic red, projector gold, and CRT teal accents over warm paper tones.",
            "Treat the page as one integrated composition, not an isolated insert illustration.",
            "Preserve declared safe zones with calmer contrast and simpler texture.",
            "Environmental lettering may appear only if tiny, natural, and subordinate to layout typography.",
        ],
        "easter_egg_rule": (
            "Optional and subtle: hide the word 'RetroVerse' only as a tiny environmental Easter egg. "
            "It must never behave like headline copy, body text, or page furniture."
        ),
        "reference_notes": {
            "legacy_canonical_title": bundle["canonical_title"],
            "legacy_canonical_byline": bundle["canonical_byline"],
            "mapped_story_id": target.story_id,
            "mapped_story_rationale": narrative_story.get("rationale"),
            "design_assignment": story_design.get("assigned_visual_role"),
            "visual_brief_name": visual_brief.get("concept_name"),
            "visual_goal": visual_brief.get("visual_goal"),
            "production_layout_type": production_target.get("layout_type"),
        },
    }

    out_path = output_path(args.year, args.page_slug, "page_brief.json")
    write_json(out_path, brief)
    print(out_path)


if __name__ == "__main__":
    main()
