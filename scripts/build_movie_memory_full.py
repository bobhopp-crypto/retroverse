from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


# Production path — all reads/writes use this only
MOVIE_MEMORY_PATH = "/Users/bobhopp/Sites/retroverse/data/movies/movie_memory.json"
SOURCE = Path(MOVIE_MEMORY_PATH)
OUTPUT = SOURCE.with_suffix(".json.tmp")
START_YEAR = 1958
END_YEAR = 2024

# Style modes: A=projection_booth, B=critic_lite, C=memory_recall
# Distribution per year (10 picks): 0-2→A, 3-5→C, 6-7→B, 8→A+C, 9→A+B
STYLE_MODE_BY_INDEX = {
    0: "A",
    1: "A",
    2: "A",
    3: "C",
    4: "C",
    5: "C",
    6: "B",
    7: "B",
    8: "AC",
    9: "AB",
}

MODE_NAMES = {
    "A": "projection_booth",
    "B": "critic_lite",
    "C": "memory_recall",
    "AC": "hybrid_A_C",
    "AB": "hybrid_A_B",
}

BANNED_PHRASES = ("this one", "this is the one", "the one that", "it works", "it follows")
BANNED_OPENINGS = {"this one", "it works", "it follows", "it's", "its"}
BANNED_PRONOUNS_AS_SUBJECT = re.compile(r"^\s*(He|She|He's|She's)\s+", re.I)
MAX_RETRIES = 3
DEBUG_OUTPUT = True


def _sentences(booth: str) -> list[str]:
    """Split into sentences, preserving content."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", booth) if s.strip()]


def _first_word(s: str) -> str:
    """First word of sentence (lowercase)."""
    m = re.match(r"^\s*(\w+)", s)
    return m.group(1).lower() if m else ""


def _normalize_for_validation(text: str) -> str:
    """Lowercase and remove punctuation for substring checks."""
    lowered = text.lower()
    return re.sub(r"[^\w\s]", " ", lowered)


def validate_projection_booth(text: str, title: str) -> tuple[bool, list[str]]:
    """Validate text against hard constraints. Returns (pass, list of failures)."""
    failures: list[str] = []
    normalized = _normalize_for_validation(text)

    for phrase in BANNED_PHRASES:
        phrase_norm = _normalize_for_validation(phrase).strip()
        if phrase in text.lower() or (phrase_norm and phrase_norm in normalized):
            failures.append(f"banned phrase: '{phrase}'")

    if BANNED_PRONOUNS_AS_SUBJECT.search(text):
        failures.append("starts with he/she as subject")

    sents = _sentences(text)
    if len(sents) >= 2:
        words = [_first_word(s) for s in sents[:3]]
        if len(set(words)) < len(words):
            failures.append("repetitive sentence openings")

    pronoun_starts = sum(1 for s in sents if _first_word(s) in ("he", "she", "it"))
    if pronoun_starts > len(sents) // 2:
        failures.append("overuse of he/she/it as subject")

    return (len(failures) == 0, failures)


def _repair_banned_phrases(text: str) -> str:
    """Replace banned phrases anywhere in text."""
    lowered = text.lower()
    repairs = [
        ("this is the one", "this film"),
        ("this one", "this film"),
        ("the one that", "the film that"),
        ("it works", "the film works"),
        ("it follows", "the story follows"),
    ]
    for banned, replacement in repairs:
        if banned in lowered:
            text = re.sub(re.escape(banned), replacement, text, flags=re.I)
    return text


def _projection_booth_mode(booth: str, _moments: list[str], _takeaways: list[str]) -> str:
    """Blunt opinion, clear judgment, conversational."""
    sents = _sentences(booth)
    if len(sents) < 2:
        return booth
    for i, s in enumerate(sents):
        if any(w in s.lower() for w in ("works", "sticks", "stays", "earns", "lands", "hits", "delivers")):
            if i == 0:
                return booth
            reordered = [s] + [x for j, x in enumerate(sents) if j != i]
            return " ".join(reordered)
    return booth


def _memory_recall_mode(booth: str, moments: list[str], _takeaways: list[str]) -> str:
    """Focus on specific scenes/moments, sensory details, no overall judgment."""
    if not moments:
        return booth
    moment = moments[0]
    sents = _sentences(booth)
    if not sents:
        return booth
    if moment.lower() in sents[0].lower():
        return booth
    rest = " ".join(sents[1:]) if len(sents) > 1 else ""
    # Avoid "The Ferris" when moment starts with proper noun
    if moment and moment[0].isupper():
        leads = (
            f"{moment}—that's the image that sticks. ",
            f"{moment}—what people remember first. ",
            f"The moment: {moment}. ",
        )
    else:
        leads = (
            f"The {moment}—that's the image that sticks. ",
            f"What stays: the {moment}. ",
            f"The {moment} is what people remember first. ",
        )
    lead = leads[hash(booth) % len(leads)]
    tail = sents[0] + (" " + rest if rest else "")
    if tail and not tail[0].isupper():
        tail = tail[0].upper() + tail[1:]
    return (lead + tail).strip()


def _critic_lite_mode(booth: str, _moments: list[str], takeaways: list[str]) -> str:
    """Balanced, thoughtful, slightly structured but natural."""
    sents = _sentences(booth)
    if len(sents) >= 2:
        return booth
    if takeaways and len(sents) == 1:
        takeaway = takeaways[0]
        return f"What stands out: {takeaway}. {sents[0]}"
    return booth


def _hybrid_ac_mode(booth: str, moments: list[str], takeaways: list[str]) -> str:
    """Combine memory_recall + projection_booth."""
    result = _memory_recall_mode(booth, moments, takeaways)
    return _projection_booth_mode(result, moments, takeaways)


def _hybrid_ab_mode(booth: str, moments: list[str], takeaways: list[str]) -> str:
    """Combine projection_booth + critic_lite."""
    result = _projection_booth_mode(booth, moments, takeaways)
    return _critic_lite_mode(result, moments, takeaways)


def _apply_mode_transform(
    booth: str,
    mode: str,
    moments: list[str],
    takeaways: list[str],
) -> str:
    """Apply mode-specific transformation. Returns styled text."""
    if mode == "A":
        return _projection_booth_mode(booth, moments, takeaways)
    if mode == "B":
        return _critic_lite_mode(booth, moments, takeaways)
    if mode == "C":
        return _memory_recall_mode(booth, moments, takeaways)
    if mode == "AC":
        return _hybrid_ac_mode(booth, moments, takeaways)
    if mode == "AB":
        return _hybrid_ab_mode(booth, moments, takeaways)
    return booth


def _fix_opening(text: str) -> str:
    """Fix banned openings and pronoun leads."""
    lowered = text.lower()
    for banned in BANNED_OPENINGS:
        if lowered.startswith(banned + " ") or lowered.startswith(banned + ","):
            text = text[len(banned):].lstrip(" ,:")
            if text and not text[0].isupper():
                text = text[0].upper() + text[1:]
            break
    text = BANNED_PRONOUNS_AS_SUBJECT.sub("", text)
    if text and not text[0].isupper():
        text = text[0].upper() + text[1:]
    return text.strip()


def generate_movie_entry(
    pick: dict,
    mode: str,
    *,
    debug: bool = True,
    year: int | None = None,
    index: int | None = None,
) -> dict | None:
    """
    Generate styled projection_booth for a pick. Enforces style mode and hard constraints.
    Retries up to MAX_RETRIES if validation fails. Returns None if validation fails after retries.
    """
    booth = pick["projection_booth"]
    moments = pick["signature_moments"]
    takeaways = pick["audience_takeaways"]
    title = pick["film"]["title"]

    if debug and year is not None and index is not None:
        mode_name = MODE_NAMES.get(mode, mode)
        print(f"{year} - {index} - {mode_name}")

    for attempt in range(MAX_RETRIES):
        result = _apply_mode_transform(booth, mode, moments, takeaways)
        result = _repair_banned_phrases(result)
        result = _fix_opening(result)
        result = _repair_banned_phrases(result)

        ok, _failures = validate_projection_booth(result, title)
        if ok:
            return {**pick, "projection_booth": result}

        if attempt < MAX_RETRIES - 1:
            result = _repair_banned_phrases(result)
            for phrase in BANNED_PHRASES:
                result = re.sub(re.escape(phrase), "the film", result, flags=re.I)
            result = _fix_opening(result)

    return None


def build_projection_booth_text(entries: list[dict]) -> str:
    """
    Combine multiple voice modes into a single unified editorial voice.
    Structure: 1–2 sentences. Start with specific memory/scene, follow with opinion.
    Source priority: memory_recall → opening, projection_booth → judgment, critic_lite → clarity.
    Fallback: if only one entry, use as-is.
    """
    if not entries:
        return ""
    if len(entries) == 1:
        return str(entries[0].get("projection_booth") or entries[0].get("text") or "").strip()

    by_mode: dict[str, str] = {}
    for e in entries:
        mode = str(e.get("mode") or "").strip().lower()
        text = str(e.get("projection_booth") or e.get("text") or "").strip()
        if mode and text:
            by_mode[mode] = text

    memory = by_mode.get("memory_recall", "")
    projection = by_mode.get("projection_booth", "")
    critic = by_mode.get("critic_lite", "")

    opening = _sentences(memory)[0] if memory else _sentences(projection)[0] if projection else ""
    projection_sents = _sentences(projection)
    judgment = next(
        (s for s in projection_sents if any(w in s.lower() for w in ("works", "sticks", "leans", "delivers", "earns", "lands"))),
        projection_sents[-1] if projection_sents else "",
    ) if projection else ""

    if not opening:
        return projection or memory or critic or ""
    if not judgment or judgment == opening:
        return opening

    judgment_clean = judgment.strip()
    if judgment_clean.lower().startswith("it "):
        judgment_clean = "the film " + judgment_clean[3:]
    elif judgment_clean.lower().startswith("the film "):
        pass
    elif judgment_clean.startswith("The ") and len(judgment_clean) > 4:
        # Lowercase article "The" for "and the ..." flow
        judgment_clean = "the " + judgment_clean[4:]

    result = f"{opening.rstrip('.')}, and {judgment_clean}"
    sents = _sentences(result)
    if len(sents) > 2:
        result = " ".join(sents[:2])
    return result.strip()


# Static fallback for academy awards when no DB/file (ceremony year = films released that year)
STATIC_ACADEMY_AWARDS: dict[int, dict] = {
    1978: {
        "best_picture": "The Deer Hunter",
        "best_director": "Michael Cimino",
        "best_actor": "Jon Voight",
        "best_actress": "Jane Fonda",
        "nominees": ["The Deer Hunter", "Coming Home", "Heaven Can Wait", "Midnight Express", "An Unmarried Woman"],
    },
    1986: {
        "best_picture": "Platoon",
        "best_director": "Oliver Stone",
        "best_actor": "Paul Newman",
        "best_actress": "Marlee Matlin",
        "nominees": ["Platoon", "Hannah and Her Sisters", "The Mission", "A Room with a View", "Children of a Lesser God"],
    },
}

# Static fallback for top 10 when movie_memory + CATALOG both insufficient
STATIC_TOP_10_BY_YEAR: dict[int, list[str]] = {
    1978: [
        "Grease", "Superman", "Heaven Can Wait", "The Deer Hunter", "Jaws 2",
        "Animal House", "Every Which Way but Loose", "Halloween", "Hooper", "The Wiz",
    ],
}

# Static fallback for also_playing when warehouse empty (4-6 titles not in top 10)
STATIC_ALSO_PLAYING_BY_YEAR: dict[int, list[str]] = {
    1978: ["Coming Home", "Midnight Express", "An Unmarried Woman", "The Driver", "Days of Heaven"],
    1986: ["The Color of Money", "Peggy Sue Got Married", "The Mission", "Mona Lisa", "Absolute Beginners"],
}


def get_academy_awards(year: int) -> dict:
    """Return academy awards for year. File first, then static fallback."""
    result = {
        "best_picture": "",
        "best_director": "",
        "best_actor": "",
        "best_actress": "",
        "nominees": [],
    }
    try:
        awards_path = SOURCE.parent.parent / "support" / "magazine" / "academy_awards.json"
        if awards_path.exists():
            data = json.loads(awards_path.read_text(encoding="utf-8"))
            y = data.get(str(year), {})
            if y:
                result["best_picture"] = y.get("best_picture", "")
                result["best_director"] = y.get("best_director", "")
                result["best_actor"] = y.get("best_actor", "")
                result["best_actress"] = y.get("best_actress", "")
                result["nominees"] = list(y.get("nominees", []))
    except (json.JSONDecodeError, OSError, KeyError):
        pass
    if not result["best_picture"] and not result["nominees"] and year in STATIC_ACADEMY_AWARDS:
        s = STATIC_ACADEMY_AWARDS[year]
        result["best_picture"] = s.get("best_picture", "")
        result["best_director"] = s.get("best_director", "")
        result["best_actor"] = s.get("best_actor", "")
        result["best_actress"] = s.get("best_actress", "")
        result["nominees"] = list(s.get("nominees", []))
    return result


def get_catalog_additional(year: int, exclude: set[str], count: int = 5) -> list[str]:
    """Return 4-6 titles from CATALOG not in exclude. Fallback to static if needed."""
    candidates: list[str] = []
    if year in CATALOG:
        for p in CATALOG[year]:
            t = (p.get("film") or {}).get("title", "").strip()
            if t and t not in exclude:
                candidates.append(t)
    if not candidates and year in STATIC_ALSO_PLAYING_BY_YEAR:
        candidates = [t for t in STATIC_ALSO_PLAYING_BY_YEAR[year] if t not in exclude]
    unique = list(dict.fromkeys(candidates))
    k = min(6, max(4, min(count, len(unique))))
    return unique[:k]


def _load_also_playing_candidates(year: int, exclude_titles: set[str]) -> list[str]:
    """Load 4–6 films not in top 10. Returns [] if no additional source."""
    warehouse = SOURCE.parent.parent / "raw" / "screen-culture" / "warehouse"
    for name in ("movies_by_year.json", "movies_master.json"):
        path = warehouse / name
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        candidates: list[str] = []
        if name == "movies_by_year":
            year_data = data.get(str(year), [])
            for item in year_data if isinstance(year_data, list) else []:
                title = (item.get("title") or item.get("name") or "").strip()
                if title and title not in exclude_titles:
                    candidates.append(title)
        else:
            records = data.get("records", [])
            for r in records:
                if r.get("year") == year:
                    title = (r.get("title") or "").strip()
                    if title and title not in exclude_titles:
                        candidates.append(title)
        if candidates:
            unique = list(dict.fromkeys(candidates))
            k = min(6, max(4, len(unique)))
            return unique[:k]
    return []


def _load_movie_memory() -> dict:
    """Load movie_memory.json. Returns {} if missing."""
    if not SOURCE.exists():
        return {}
    with SOURCE.open(encoding="utf-8") as fh:
        return json.load(fh)


def _select_cult_film(films: list[dict]) -> dict | None:
    """
    Select ONE film for cult classic sidebar.
    Prefer: Cult Favorite > Underrated > The One That Grows on You > recognizable/unique title.
    Fallback: films[0].
    """
    if not films:
        return None
    cult_categories = ("Cult Favorite", "Underrated", "The One That Grows on You")
    for cat in cult_categories:
        for f in films:
            if f.get("category") == cat:
                return f
    return films[0]


def build_movies_charts_page(year: int, *, debug: bool = True) -> dict:
    """
    Build Movies Charts page: top 10, academy awards, also playing.
    Data-driven, not narrative.
    """
    data = _load_movie_memory()
    key = str(year)
    picks = (data.get(key) or {}).get("picks", [])

    if len(picks) < 10 and year in CATALOG:
        picks = CATALOG[year]

    if len(picks) < 10 and year in STATIC_TOP_10_BY_YEAR:
        titles = STATIC_TOP_10_BY_YEAR[year][:10]
        top_10 = [{"rank": i, "title": t} for i, t in enumerate(titles, start=1)]
    else:
        top_10 = [
            {"rank": i, "title": p.get("film", {}).get("title", "").strip()}
            for i, p in enumerate(picks[:10], start=1)
        ]

    exclude = {t["title"] for t in top_10 if t.get("title")}
    also_playing = _load_also_playing_candidates(year, exclude)
    if not also_playing:
        also_playing = get_catalog_additional(year, exclude=exclude, count=5)

    academy = get_academy_awards(year)

    top_10_titles = {t["title"] for t in top_10 if t.get("title")}
    nominee_titles = set(academy.get("nominees") or [])
    overlap = top_10_titles & nominee_titles

    page = {
        "page_type": "movies_charts",
        "year": year,
        "headline": "Movies & Awards",
        "top_10_movies": top_10,
        "academy_awards": academy,
        "also_playing": also_playing,
        "insights": {
            "box_office_vs_awards_overlap": len(overlap),
            "overlap_titles": sorted(overlap),
        },
    }

    if debug:
        awards_ok = bool(academy.get("best_picture") or academy.get("nominees"))
        print(f"Charts Data:")
        print(f"  Top 10: {len(top_10)}")
        print(f"  Awards: {'populated' if awards_ok else 'empty'}")
        print(f"  Also Playing: {len(also_playing)}")

    return page


def build_projection_booth_page(year: int, *, debug: bool = True) -> dict:
    """
    Build Projection Booth editorial page with films and Cult Classic sidebar.
    Returns: {headline, films, cult_classic?}
    """
    data = _load_movie_memory()
    key = str(year)
    cult_year = year - 20
    cult_key = str(cult_year)

    picks = (data.get(key) or {}).get("picks", [])
    films = []
    for pick in picks:
        entries = get_projection_booth_entries_for_pick(pick)
        text = build_projection_booth_text(entries)
        films.append({
            "title": pick.get("film", {}).get("title", ""),
            "year": pick.get("film", {}).get("year", year),
            "category": pick.get("category", ""),
            "text": text,
        })

    page: dict = {
        "headline": "From the Projection Booth",
        "intro": "A few that stuck, a few that surprised people, and one that never really left.",
        "films": films,
    }

    cult_picks = (data.get(cult_key) or {}).get("picks", [])
    if cult_picks:
        cult_film = _select_cult_film(cult_picks)
        if cult_film:
            cult_entries = get_projection_booth_entries_for_pick(cult_film)
            cult_text = build_projection_booth_text(cult_entries)
            cult_title = cult_film.get("film", {}).get("title", "")
            page["cult_classic"] = {
                "label": f"Cult Classic — {cult_year}",
                "title": cult_title,
                "text": cult_text,
            }
            if debug:
                print(f"Cult Classic:\n{year} -> {cult_year}\nSelected: {cult_title}")

    return page


def get_projection_booth_entries_for_pick(pick: dict) -> list[dict]:
    """
    Generate all mode variants for a pick. Returns list of {mode, projection_booth}.
    Use with build_projection_booth_text() for unified voice.
    """
    booth = pick.get("projection_booth", "")
    moments = pick.get("signature_moments", [])
    takeaways = pick.get("audience_takeaways", [])
    entries = []
    for mode_key, mode_name in [("C", "memory_recall"), ("A", "projection_booth"), ("B", "critic_lite")]:
        text = _apply_mode_transform(booth, mode_key, moments, takeaways)
        if text:
            entries.append({"mode": mode_name, "projection_booth": text})
    return entries


def entry(
    category: str,
    title: str,
    year: int,
    signature_moments: list[str],
    audience_takeaways: list[str],
    projection_booth: str,
) -> dict:
    return {
        "category": category,
        "film": {"title": title, "year": year},
        "signature_moments": signature_moments,
        "audience_takeaways": audience_takeaways,
        "projection_booth": projection_booth,
    }


CATALOG_TEXT = """
# 1958
1958|Crowd Favorite|Gigi|garden parties with Gigi~carriage rides through Paris~Maxim's entrance~Gaston seeing the room differently|lush production~old-world glamour~memorable songs~romantic pull|Gaston keeps drifting through salons and carriage rides until Gigi walks into Maxim's and changes the room. Gigi is mostly remembered for Paris, gowns, and that entrance.
1958|After Midnight|Cat on a Hot Tin Roof|Brick on the crutch~family birthday dinner~Big Daddy bedroom talk~Maggie circling the truth|heated family drama~sharp dialogue~star chemistry~tense atmosphere|The birthday gathering keeps getting tighter, and Brick on that crutch gives every scene extra strain. Cat on a Hot Tin Roof sticks because the room never really cools off.
1958|Big Screen Moment|South Pacific|Bali Ha'i arrival~beachside songs~Thanksgiving show~wartime flights and departures|large musical scale~color-drenched images~recognizable songs~sweeping mood|South Pacific goes wide with islands, uniforms, and those sudden washes of color. People usually remember the songs first, then the feeling of the whole picture filling the screen.
1958|Rewatchable|The Vikings|longship arrival~oar-driven sea attack~feast hall clashes~cliffside duel|old-school spectacle~rough adventure tone~physical action~big costumes|The longships, the helmets, and that cliffside fight are the parts that come back first. The Vikings has a blunt, charging-forward energy that makes another pass easy.
1958|Cult Favorite|The Blob|first strange discovery~diner panic~movie theater stampede~teenagers trying to warn town|small-town panic~simple concept~drive-in energy~sticky imagery|A small blob on the ground turns into theater panic and people running for the exits. The Blob is pure drive-in memory, right down to the crowd scenes.
1958|Date Night|Bell Book and Candle|Greenwich Village shop scenes~cat familiar appearing nearby~nightclub visits~spell-driven romance|playful charm~Manhattan style~cocktail-hour mood~star chemistry|Kim Novak and James Stewart give Bell Book and Candle that late-night Manhattan glow. The shop, the cat, and the nightclub mood are what people keep hold of.
1958|Underrated|The Defiant Ones|chain gang escape~crossing fields while chained~river crossing~truck stop tension|two-hander tension~social edge~raw performances~forward momentum|Two men who do not want each other are stuck moving in the same direction from the first escape on. The Defiant Ones stays memorable because every step feels forced and personal.
1958|The One That Grows on You|Touch of Evil|opening car-bomb tracking shot~border-town nightlife~motel stakeout~Quinlan working the scene|thick noir mood~restless camera~border-town grime~crooked power|That opening tracking shot gets mentioned first, but the motel stakeout and the whole border-town feeling are what settle in later. Touch of Evil gets dirtier and more interesting the longer it sits around in memory.
1958|Crowd Favorite|Vertigo|rooftop chase~following Madeleine through San Francisco~sequoia grove visit~bell tower climb|dreamlike mood~obsessive pull~San Francisco atmosphere~images that linger|Scottie trails Madeleine across San Francisco, and people remember the bay, the flowers, and that climb up the bell tower. Vertigo keeps floating between romance and dread, which is why the images stay put.
1958|After Midnight|A Night to Remember|ship departure~iceberg warning~lifeboat loading~band playing on deck|mounting dread~procedural detail~ensemble focus~quiet power|A Night to Remember plays like people trying to stay organized while the deck keeps tilting against them. The iceberg warning, the lifeboats, and the band are usually the pieces that come right back.

# 1959
1959|Crowd Favorite|Ben-Hur|galley slavery scenes~chariot race setup~arena race itself~crowd roaring from the stands|epic scale~muscular action~iconic set piece~old Hollywood sweep|Ben-Hur carries a lot of size even before the chariot race shows up. Once the arena sequence starts, the whole movie is locked in around that memory.
1959|After Midnight|Anatomy of a Murder|small-town defense prep~courtroom objections~jazz-bar stops~witness testimony turns|legal tension~smart dialogue~grown-up tone~strong performances|James Stewart working the courtroom is the center of the whole thing, but the side trips and little strategy beats give Anatomy of a Murder its shape. The picture feels sly instead of flashy.
1959|Big Screen Moment|North by Northwest|United Nations scramble~crop-duster attack~train dining-car flirtation~Mount Rushmore chase|showman pacing~set-piece thrills~slick style~constant movement|Everybody brings up the crop duster, then the scramble across Mount Rushmore right behind it. North by Northwest keeps moving with enough style that the big moments never feel isolated.
1959|Rewatchable|Rio Bravo|jail watched from across street~Dean Martin's return to form~hotel-room standoffs~final shootout setup|easy ensemble chemistry~hangout western feel~clear stakes~dry humor|Rio Bravo has plenty of gunplay, but the hanging around is what people end up liking. The sheriff's office, the songs, and the slow build with that group make the whole thing inviting.
1959|Cult Favorite|House on Haunted Hill|guests entering the mansion~skeleton prank sequence~basement discoveries~nighttime panic in the halls|gimmicky fun~campy chills~haunted-house appeal~party-movie energy|House on Haunted Hill is remembered like a Halloween party that keeps getting stranger room by room. The mansion, the skeleton, and Vincent Price's voice do most of the work.
1959|Date Night|Pillow Talk|party-line mix-ups~interior design scenes~split-screen phone calls~identity game between leads|bright chemistry~city sophistication~playful banter~romantic comedy snap|Doris Day and Rock Hudson spend Pillow Talk turning phone calls into a whole game. The split-screen bits and all that apartment style are the first things people mention.
1959|Underrated|Imitation of Life|mother-daughter clashes~stage career taking off~prom confrontation~funeral sequence atmosphere|big emotions~melodramatic force~strong performances~social weight|Imitation of Life does not hide its feelings for a second, and that directness is part of the pull. The family blowups and the final procession are the images that tend to stay.
1959|The One That Grows on You|The 400 Blows|classroom rebellion~carnival spin ride~Paris drifting scenes~run toward the shore|restless youth perspective~natural feeling~bittersweet mood~lasting final image|Jean-Pierre Leaud running through the city gives The 400 Blows its shape. The school trouble, the spinning ride, and the run to the water keep gaining weight later.
1959|Crowd Favorite|Some Like It Hot|train ride in disguise~Sugar on the ukulele~hotel-room chaos~yacht scenes|comic timing~fast banter~perfect ensemble rhythm~rewatch value|The train, the ukulele, and people ducking in and out of rooms are the pieces everybody grabs first. Some Like It Hot moves so lightly that the whole setup still feels fresh.
1959|After Midnight|Black Orpheus|carnival crowds~streetcar and hillside views~guitar serenades~descent into the ritual spaces|music-driven mood~mythic feeling~vivid color~romantic melancholy|Black Orpheus is all carnival movement and hillside color until the story turns more haunted. The music and the city are what make the memory hold.

# 1960
1960|Crowd Favorite|Psycho|Marion at the motel~shower sequence~staircase investigation~house on the hill|shock value~tight suspense~iconic imagery~nerve-jangling score|The motel sign, the shower curtain, and that house on the hill are enough to pull Psycho right back into focus. Hitchcock keeps the whole thing tense without ever letting it feel busy.
1960|After Midnight|The Apartment|late-night office borrowings~key exchange routine~holiday party fallout~quiet apartment conversations|bittersweet tone~smart writing~lonely city feeling~human scale|The Apartment remembers the key exchange almost like a bad office joke that keeps getting sadder. Jack Lemmon and Shirley MacLaine give the whole picture a bruised warmth.
1960|Big Screen Moment|Spartacus|gladiator training~arena combat~slave march across open land~battle formations lining the hills|epic sweep~muscular action~historical scale~heroic momentum|Spartacus goes big with training yards, battle lines, and crowds looking down from the stands. The scale is the draw, but Kirk Douglas keeps the center sturdy.
1960|Rewatchable|The Magnificent Seven|gunfighters gathering~village defense planning~training the farmers~ride into the final fight|cool ensemble~western swagger~clean action~great music|The Magnificent Seven is all about getting the group together and watching them settle into place. Once Elmer Bernstein's score kicks in, the whole ride gets easier to revisit.
1960|Cult Favorite|Peeping Tom|studio camera tests~night shoots through London~mirror-lined room~screening the footage alone|uncomfortable tension~ahead-of-its-time style~psychological chill~queasy intimacy|Peeping Tom gets under the skin by turning the camera itself into the problem. The studio spaces and those private screenings are what make it linger.
1960|Date Night|Bells Are Ringing|switchboard mix-ups~party scenes in the city~phone calls turning personal~elevator and apartment flirtation|bright songs~romantic energy~city sparkle~easy charm|Bells Are Ringing has that Manhattan musical bounce from the first switchboard gag on. Judy Holliday and Dean Martin keep the romance light on its feet.
1960|Underrated|Inherit the Wind|town square arrival~courtroom sparring~Bible and science arguments~closing walk from the courthouse|ideas in plain language~actor showcase~steady tension~small-town atmosphere|The courtroom arguments are the obvious pull, but Inherit the Wind also remembers the heat of the town around them. Spencer Tracy and Fredric March give every exchange some bite.
1960|The One That Grows on You|Purple Noon|Mediterranean boat trip~forged signatures and letters~lazy seaside villa scenes~cat-and-mouse social games|sunlit menace~cool surfaces~slow-burn suspense~stylish mood|Purple Noon looks relaxed for a long time, which is exactly why it gets more unsettling later. The boat, the villa, and Alain Delon's blank calm keep returning.
1960|Crowd Favorite|Ocean's 11|casino floor scouting~coordinated Las Vegas plan~New Year's Eve blackout~Rat Pack walking the Strip|cool-star energy~nightlife appeal~easy confidence~hangout fun|Ocean's 11 is remembered as much for the Strip and the suits as for the heist itself. Watching that group move through Vegas is half the point.
1960|After Midnight|Breathless|stolen car escape~street wandering with Patricia~bedroom talk in the apartment~newsstands and boulevards|freewheeling style~modern energy~jump-cut rhythm~casual cool|Breathless feels like it is making itself up while it walks down the street. The apartment scenes and the loose Paris movement are what stay behind.

# 1961
1961|Crowd Favorite|West Side Story|gym dance~Tonight on the fire escape~rumble setup under the highway~America on the rooftop|big musical emotion~street-corner energy~famous songs~visual punch|West Side Story remembers the gym first, then the fire escapes and the rooftop singing right after. The whole picture keeps emotion and movement in the same place.
1961|After Midnight|The Hustler|opening pool challenge~smoke-filled back rooms~Sarah and Eddie talking alone~high-stakes rematch|hard-edged drama~great performances~nighttime atmosphere~psychological strain|The Hustler is all felt hats, cigarette smoke, and people trying to stare each other down over a pool table. Paul Newman gives the whole thing a live-wire edge.
1961|Big Screen Moment|The Guns of Navarone|cliff climb at night~island infiltration~gun emplacements revealed~escape under fire|mission tension~adventure scale~rugged settings~ensemble grit|The climb up the cliff is the part nearly everybody recalls, and the island mission keeps that pressure on. The Guns of Navarone has a big, rough travel-movie feel.
1961|Rewatchable|One Hundred and One Dalmatians|Cruella's first entrance~television rescue call~snowy cross-country journey~puppies covering themselves in soot|memorable villain~fast family pacing~distinct animation~playful suspense|Cruella de Vil walking through the door is enough to bring the whole movie back. One Hundred and One Dalmatians moves quickly and keeps the peril light on its feet.
1961|Cult Favorite|The Innocents|governess hearing voices at night~children by the lake~apparition in the garden~candlelit hallways|ghostly atmosphere~psychological uncertainty~beautiful black-and-white~quiet dread|The Innocents gets under the skin with whispered rooms and sudden figures at a distance. The lake and the candlelit hallways are what people keep picturing.
1961|Date Night|Breakfast at Tiffany's|Holly in front of Tiffany's~rainy alley cat scene~party in the apartment~Moon River by the window|urban romance~star appeal~famous style~bittersweet charm|Breakfast at Tiffany's has the little black dress, the party, and that window song locked into popular memory. Audrey Hepburn gives the movie its whole weather system.
1961|Underrated|A Raisin in the Sun|family crowded in the apartment~insurance check debates~younger generation clashing~visitors testing the room|strong ensemble~social immediacy~room-size intensity~emotional honesty|A Raisin in the Sun stays inside that apartment and turns every doorway into pressure. The arguments around the check are what people remember, but the family feeling is what lasts.
1961|The One That Grows on You|Yojimbo|stranger entering town~gangs facing off across the street~silk merchant chaos~swordplay after long stillness|dry humor~lean storytelling~samurai cool~clever strategy|Yojimbo introduces one dusty street and gets a whole world out of it. Toshiro Mifune's sideways grin and the gang standoffs get better the more time passes.
1961|Crowd Favorite|The Parent Trap|summer camp rivalry~split-screen tricks~switching places at home~dance on the patio|family fun~clever setup~star charm~light comic pace|The camp feud and the switcheroo are the hooks everybody knows, and the split-screen still has plenty of charm. The Parent Trap carries easy vacation energy from start to finish.
1961|After Midnight|Splendor in the Grass|school dance moments~picnic by the waterfall~family pressure closing in~lonely Kansas walks|aching romance~youthful intensity~beautiful leads~emotional fallout|Splendor in the Grass hangs on young faces trying to stay composed while everything around them says otherwise. The picnic, the dances, and the quiet walks are the scenes people pull back up.

# 1962
1962|Crowd Favorite|Lawrence of Arabia|desert crossing on camelback~match-cut into the dunes~attack on Aqaba~riders stretching across the horizon|immense scale~striking imagery~heroic mythmaking~desert atmosphere|Lawrence of Arabia is remembered in big shapes: a match blown out, riders on the horizon, and all that sand opening up. The scale is so complete that even the quiet stretches feel huge.
1962|After Midnight|To Kill a Mockingbird|Atticus in the courtroom~children watching from the balcony~night visit to the jail~small-town streets after dark|moral clarity~quiet tension~warm family core~actor showcase|The courtroom is the center, but the porch scenes and the night outside the jail are just as important to the memory. To Kill a Mockingbird keeps its voice calm without ever going soft.
1962|Big Screen Moment|The Longest Day|paratroopers dropping at night~beach landings~troops pushing inland~commanders tracking the invasion|battle scale~multi-front tension~ensemble reach~historical sweep|The Longest Day is almost all movement, from the night drops to the beaches filling up with bodies and equipment. The movie feels built to be watched wide.
1962|Rewatchable|Dr. No|first trip to Jamaica~Crab Key approach~dragon tank scare~Bond meeting Honey Ryder on the beach|cool hero appeal~spy-movie snap~exotic locations~clean pacing|Dr. No gets the Bond template in place fast with casinos, island danger, and Sean Connery walking through it all like he owns the frame. Honey Ryder coming out of the water is one of those images that never left.
1962|Cult Favorite|Whatever Happened to Baby Jane?|Jane's old vaudeville routine~dinner tray horror~sisters trapped inside the house~neighbors almost learning too much|camp and cruelty~actor fireworks~claustrophobic setting~uneasy humor|Bette Davis turns every room into a stage, which is why the house feels more warped every minute. Whatever Happened to Baby Jane? is remembered for the act, the makeup, and the mean little details.
1962|Date Night|The Music Man|arrival in River City~Seventy-Six Trombones parade~library flirtation~town turning toward the big show|show tunes that stick~big ensemble bounce~small-town warmth~romantic charm|The Music Man is all parade rhythm, fast talk, and townspeople getting swept up before they know better. That library flirtation gives the picture its softer center.
1962|Underrated|Days of Wine and Roses|first dates at parties~domestic scenes getting shakier~flowers and quiet mornings~room-by-room consequences|adult drama~performance driven~sad honesty~ordinary-life detail|Days of Wine and Roses keeps returning to small household moments, which is what makes it hit. Jack Lemmon and Lee Remick make the whole slide feel painfully familiar.
1962|The One That Grows on You|The Manchurian Candidate|nightmare card game~brainwashing flashbacks~political rally scenes~train ride conversations|paranoid mood~sharp satire~cold-war unease~unsettling structure|The nightmare sequence is the doorway into the whole movie, and it stays strange no matter how many years pass. The Manchurian Candidate gets more unnerving as the political scenes pile up.
1962|Crowd Favorite|Cape Fear|Max Cady on the sidewalk~bowling alley surveillance~nighttime river trip~Sam Bowden trying to stay ahead|threat right out front~tight suspense~strong villain~small-town menace|Cape Fear remembers Robert Mitchum standing there and making every ordinary place look worse. The river trip and the constant watching are what keep the tension alive.
1962|After Midnight|Jules and Jim|bohemian running scenes~bridge and bicycle stretches~shifting love triangle~country house visits|free-flowing style~romantic melancholy~restless energy~memorable faces|Jules and Jim feels like a memory already in motion, especially in the running and cycling scenes. The picture stays light on its feet even while the feelings get messier.

# 1963
1963|Crowd Favorite|The Great Escape|motorcycle jump setup~tunnel digging operations~forged papers and disguises~mass breakout across the fields|great ensemble~mission momentum~iconic set piece~wartime cool|The tunnels, the forged papers, and Steve McQueen on that motorcycle are the pieces everyone grabs first. The Great Escape has so much forward motion that the long runtime barely registers.
1963|After Midnight|Hud|cattle crisis on the ranch~father-son clashes~late-night kitchen tension~dusty Texas roads|hard-edged performances~moral friction~stark black-and-white~dry atmosphere|Hud is remembered for the look in Paul Newman's eyes as much as anything he says. The ranch scenes keep turning family arguments into something colder and meaner.
1963|Big Screen Moment|Cleopatra|entry into Rome~barge and palace spectacle~crowd scenes in the city~armies and pageantry on display|lavish scale~ornate production~star power~old-Hollywood excess|Cleopatra keeps finding another curtain to pull back and another staircase to fill with people. The movie is remembered for size first and story second.
1963|Rewatchable|Charade|ski resort opening~market and rooftop chase~shower surprise~Paris cat-and-mouse flirtation|light suspense~movie-star chemistry~travel glamour~comic touch|Charade moves like a mystery and a flirtation at the same time. Paris, Audrey Hepburn's wardrobe, and Cary Grant's timing make the whole thing easy to revisit.
1963|Cult Favorite|The Birds|schoolyard crows gathering~gas station explosion~phone booth attack~house boarded up at night|pure tension~simple premise pushed hard~memorable imagery~escalating panic|The image of crows lining up behind the playground is enough to pull The Birds right back. Hitchcock keeps making everyday places feel exposed.
1963|Date Night|Tom Jones|meal with the camera close in~run through the countryside~inn-room mix-ups~fencing and flirtation|playful energy~period charm~cheeky tone~romantic mischief|Tom Jones is remembered for appetite, movement, and everybody chasing somebody through a door. The whole movie has a wink without losing its rhythm.
1963|Underrated|Lilies of the Field|traveling handyman arrival~chapel plans taking shape~nuns working the land~songs around the build|warm spirit~actor showcase~small-scale uplift~human humor|Sidney Poitier carries Lilies of the Field with easy confidence from the first arrival onward. The building of the chapel is simple on paper, but those scenes stay with people.
1963|The One That Grows on You|8 1/2|dreamlike traffic jam opening~film set confusion~women in memory and fantasy~circus-like finale mood|creative chaos~visual imagination~autobiographical feel~layers to unpack|8 1/2 throws a traffic jam dream at you right away and never goes back to anything ordinary. The film set confusion and floating memories get richer with distance.
1963|Crowd Favorite|It's a Mad, Mad, Mad, Mad World|desert car crash confession~reckless road race~hardware store destruction~airport chase pieces|big ensemble comedy~escalating chaos~old-school stunt work~crowd-pleasing pace|The treasure chase keeps throwing more vehicles, more yelling, and more broken property onto the screen. That giant-comedy energy is the whole reason the movie is remembered.
1963|After Midnight|From Russia with Love|train compartment fight~helicopter chase~gypsy camp attack~Bond in Istanbul with the case|sleek spy atmosphere~travel appeal~grounded action~cold-war intrigue|From Russia with Love feels leaner and meaner than a lot of Bond pictures that came later. The train fight and the Istanbul sections are the pieces most people hold onto.

# 1964
1964|Crowd Favorite|Mary Poppins|umbrella arrival from the sky~Jolly Holiday chalk world~Step in Time on the rooftops~tea party on the ceiling|family magic~big songs~visual playfulness~boundless charm|Mary Poppins has the umbrella, the chalk world, and the rooftop dance all sitting in plain view. Julie Andrews gives the whole movie its lift.
1964|After Midnight|Dr. Strangelove|war room debates~B-52 crew heading toward target~riding the bomb image~Strangelove fighting the wheelchair|jet-black comedy~sharp satire~iconic performances~cold-war nerves|The war room table and that final airborne image are enough to summon Dr. Strangelove in seconds. Kubrick keeps the absurdity bone dry the whole way.
1964|Big Screen Moment|Goldfinger|laser table threat~Fort Knox buildup~Aston Martin gadgets~golf match that turns into a duel|pop spy glamour~big set pieces~memorable villain~clean fun|Goldfinger is packed with moments people can name on sight, from the laser table to the Aston Martin. The movie moves with the confidence of a hit that knows it.
1964|Rewatchable|A Hard Day's Night|train-car clowning~running through the field~television studio chaos~concert finale energy|infectious pace~funny banter~music-driven rush~youthful bounce|A Hard Day's Night runs on pure momentum from the train to the field to the TV studio. The Beatles are funny enough on their own that the whole thing keeps replay value.
1964|Cult Favorite|The Masque of the Red Death|colored chamber rooms~masked revels in the castle~Vincent Price toying with guests~red-cloaked figure appearing|gothic mood~vivid color~macabre pageantry~dreamy horror|The castle rooms and the masked revels are what stick first, then Vincent Price's voice right behind them. The Masque of the Red Death feels like a horror mural.
1964|Date Night|My Fair Lady|Ascot racecourse scene~embassy ball transformation~rain in Spain rehearsal~Covent Garden opening|lavish musical style~star costumes~romantic push-pull~famous songs|My Fair Lady is remembered in hats, gowns, and that embassy ballroom. Audrey Hepburn and Rex Harrison keep the whole picture lively even when the sets are doing a lot of the talking.
1964|Underrated|Zulu|defensive line at the station~singing across the battlefield~waves of attacks~quiet officers planning the hold|battle tension~disciplined staging~ensemble grit~wide-open scope|Zulu gets its power from seeing a tiny station boxed in by open land and gathering danger. The back-and-forth singing across the lines is the part many people never forget.
1964|The One That Grows on You|The Umbrellas of Cherbourg|umbrella shop in bright color~gas station goodbye~letters from far away~chance meeting years later|through-sung mood~color design~heartache in plain view~melodic flow|The Umbrellas of Cherbourg lands through color and melody before anything else. The shop, the gas station, and the way people sing ordinary pain keep coming back later.
1964|Crowd Favorite|The Pink Panther|animated title sequence~ski resort farce~jewel theft confusion~Peter Sellers wandering into every scene sideways|comic silliness~iconic character work~light caper feel~rewatch value|The title music starts and people already know the mood. Peter Sellers makes The Pink Panther feel like a chain of favorite bits instead of a puzzle to solve.
1964|After Midnight|Band of Outsiders|cafe dance scene~running through the Louvre~apartment robbery plot~quiet aimless Paris wandering|casual cool~new-wave looseness~youthful drift~moments over plot|Band of Outsiders is mostly remembered through the cafe dance and the sprint through the Louvre. Godard lets the hanging around become the main attraction.

# 1965
1965|Crowd Favorite|The Sound of Music|opening on the hillside~Do-Re-Mi around Salzburg~children singing goodbye at the party~festival performance|beloved songs~scenic beauty~family warmth~sweeping emotion|The hills, the songs, and the children lined up in those outfits are enough to bring The Sound of Music right back. Julie Andrews carries the whole thing with bright authority.
1965|After Midnight|Doctor Zhivago|train in the snow~candlelit house of ice~crowded wartime streets~Lara and Zhivago crossing paths again|sweeping romance~winter imagery~historical melancholy~big emotional canvas|Doctor Zhivago is remembered in snow, candlelight, and Omar Sharif looking like he got swept into history by mistake. The movie's sense of scale never loses the personal ache.
1965|Big Screen Moment|Thunderball|underwater battle~jetpack opening escape~casino scenes in Nassau~rescue on the waves|large action scenes~tropical locations~spy spectacle~easy cool|Thunderball goes big with the underwater fight and never really apologizes for it. The whole picture feels built around sun, gear, and Sean Connery walking into danger without much strain.
1965|Rewatchable|Cat Ballou|train robbery turns sideways~Lee Marvin doing double duty~musical narration~ragtag revenge push|comic western flavor~loose fun~memorable performance~easy rhythm|Cat Ballou keeps finding another oddball turn just when the story threatens to settle down. Lee Marvin gives the movie most of its crooked grin.
1965|Cult Favorite|Repulsion|cracks appearing in the walls~hallway hands reaching out~empty apartment growing stranger~razor and mirror unease|psychological horror~claustrophobic feeling~minimalist dread~disturbing images|Repulsion does not need much more than one apartment and a bad silence to get under the skin. The walls, the hands, and Catherine Deneuve's distant stare are the parts people recall.
1965|Date Night|A Patch of Blue|park bench meetings~city walks together~quiet conversations at home~music lessons and small gifts|tender chemistry~gentle pace~emotional sincerity~soft city atmosphere|A Patch of Blue remembers the walks and the bench scenes more than anything dramatic. Sidney Poitier and Elizabeth Hartman give the movie an unusual calm.
1965|Underrated|Darling|fashion shoots and photo sessions~parties with too much polish~marriage drifting offscreen~London nightlife whirl|sharp social observation~mod style~restless energy~star turn|Julie Christie glides through Darling like she is always already on her way to the next room. The shoots, the parties, and the empty glamour are what stay behind.
1965|The One That Grows on You|For a Few Dollars More|watch duel motif~bounty hunters sizing each other up~bank robbery aftermath~graveyard showdowns in dusty towns|western cool~musical hooks~slow-burn tension~double-lead chemistry|For a Few Dollars More takes its time with glances, watches, and men deciding when to move. The movie gets better once those rhythms lock in.
1965|Crowd Favorite|The Great Race|pie fight~Arctic ice block rescue~elaborate car rally start~palace and swordplay chaos|big comic scale~old-fashioned fun~stunt-heavy energy~star charisma|The Great Race throws so much physical comedy at the screen that the pie fight still towers over the rest. Jack Lemmon and Tony Curtis keep the pace lively.
1965|After Midnight|Faster, Pussycat! Kill! Kill!|desert drag race~go-go dancing introduction~roadside confrontations~isolated ranch showdown|exploitative swagger~loud energy~cult attitude~pop-art surface|Faster, Pussycat! Kill! Kill! announces itself with a drag race and never lowers its voice. The desert, the dancing, and the attitude are the whole appeal.

# 1966
1966|Crowd Favorite|The Good, the Bad and the Ugly|three-way standoff setup~bridge blown in battle~desert march~graveyard showdown|epic western scale~iconic music~face-to-face tension~mythic cool|The graveyard showdown gets the headlines, but the bridge and the long desert stretch give the whole movie its size. Leone keeps turning still faces into major events.
1966|After Midnight|Who's Afraid of Virginia Woolf?|late-night drinks turning mean~living-room games~car ride after the party~another round at sunrise|actor fireworks~acid dialogue~marital warfare~claustrophobic intensity|The whole movie feels like one endless bad night that nobody can walk away from. Elizabeth Taylor and Richard Burton make every line sound dangerous.
1966|Big Screen Moment|Fantastic Voyage|miniaturization sequence~travel through the bloodstream~immune system attack~laser inside the body|imaginative spectacle~science-fiction adventure~colorful design~set-piece novelty|Fantastic Voyage turns the human body into a whole adventure landscape. The shrinking scene and the trip through those bright interior spaces are what people remember.
1966|Rewatchable|Batman: The Movie|shark repellent on the helicopter ladder~villains at the table together~bomb running around the pier~Batcopter and Batboat action|pure camp fun~comic-book colors~fast gag rhythm~nostalgia pull|Batman: The Movie is remembered in gadgets, labels, and one ridiculous emergency after another. The bomb-running gag still tells you exactly what kind of fun it is.
1966|Cult Favorite|Persona|nurse and actress at the shore house~projector and burned film images~faces overlapping in close-up~confessions in the dark|art-film mystery~psychological intensity~striking imagery~unsettled mood|Persona stays in the mind through fragments: the projector, the faces, the house by the water. The movie feels like a conversation turning into a mirror.
1966|Date Night|Alfie|Alfie talking straight to camera~city nightlife and parties~car rides with different women~quiet hospital corridor shift|swinging-London style~direct address~comic and sad turns~star charm|Alfie is remembered for Michael Caine turning and talking straight at the audience as if he already knows the answer. London nightlife gives the whole picture its snap.
1966|Underrated|The Sand Pebbles|gunboat life on the river~engine-room work~street violence escalating~shore leave turning tense|river setting~period detail~moral conflict~strong atmosphere|The Sand Pebbles has a muddy, mechanical feel that stands apart from cleaner war pictures. Steve McQueen and that riverboat environment carry the memory.
1966|The One That Grows on You|A Man for All Seasons|courtroom questioning~quiet household debates~royal pressure closing in~More standing firm in plain rooms|measured tension~moral focus~precise writing~performance strength|A Man for All Seasons gets stronger later because the rooms are so plain and the choices are so sharp. Paul Scofield makes stillness feel eventful.
1966|Crowd Favorite|The Professionals|train ambush~tracking across desert country~blowing up the camp~team riding out together|adventure momentum~strong ensemble~western action~dry banter|The Professionals moves with the confidence of a picture that knows its team is the hook. The desert travel and demolition scenes are the parts people carry out.
1966|After Midnight|Blow-Up|fashion shoot in the park~darkroom enlargements~nightclub set with the Yardbirds~mime tennis at the end|cool surfaces~mystery without certainty~mod London mood~images over answers|Blow-Up is remembered through the park photographs and the darkroom more than any explanation. The whole movie hangs on what might be hiding inside a picture.

# 1967
1967|Crowd Favorite|The Graduate|airport walkway opening~seduction in the hotel room~pool and scuba visual jokes~church run and bus ride|sharp satire~iconic music use~awkward humor~youthful confusion|The Graduate remembers Benjamin under glass, in hotel hallways, and on that bus more than almost anything else. The Simon and Garfunkel songs carry half the feeling on their own.
1967|After Midnight|In the Heat of the Night|station-house interrogation~Virgil Tibbs at the mansion~small-town hostility on the road~late-night investigation turns|social tension~detective momentum~strong performances~simmering atmosphere|In the Heat of the Night keeps tightening through interrogations and ugly little roadside moments. Rod Steiger and Sidney Poitier make the whole movie feel fully awake.
1967|Big Screen Moment|Bonnie and Clyde|bank robberies in daylight~first getaway scenes~ambush paranoia on the road~Dust Bowl landscapes rushing past|outlaw energy~movie-star cool~sudden violence~new-Hollywood charge|Bonnie and Clyde hits with robberies, road dust, and two stars who look like they know the camera is watching. The movie still feels like a line being crossed.
1967|Rewatchable|The Dirty Dozen|misfit recruits meeting~training camp fights~inspection prank~raid on the chateau|tough-guy ensemble~mission setup~war-movie fun~rowdy humor|The Dirty Dozen gives you the team, the training, and the mission in a way that keeps pulling people back. Watching that bunch slowly click into place is half the pleasure.
1967|Cult Favorite|Wait Until Dark|apartment searched in the dark~photographs and dolls changing hands~telephone booth fear~lights going out for the final round|single-location suspense~great setup~nerve-jangling payoff~star performance|Wait Until Dark takes one apartment and turns it into a trap the audience can map in real time. The dark-room climax is the memory almost everybody shares.
1967|Date Night|Guess Who's Coming to Dinner|airport arrival~family dinner arguments~kitchen conversations~parents regrouping in private|warmth with bite~relationship focus~great cast~talk-driven appeal|Guess Who's Coming to Dinner is mostly remembered around the dinner table and in the rooms just off it. The movie stays lively because every person in the house has a different angle.
1967|Underrated|To Sir, with Love|classroom testing the new teacher~students out on the museum trip~hard talk about adulthood~title song over the goodbye mood|teacher-student connection~London texture~steady emotion~memorable song|To Sir, with Love remembers the classroom first, then the field trip and the title song closing in behind it. Sidney Poitier gives the whole film a calm center.
1967|The One That Grows on You|Cool Hand Luke|car-washing work line~egg-eating bet~chain-gang escapes~Luke back with the boys again|rebellious streak~dry humor~Southern atmosphere~performance charm|Cool Hand Luke sticks through one-off moments like the eggs and the car wash, then keeps deepening after that. Paul Newman makes refusal look almost casual.
1967|Crowd Favorite|The Jungle Book|Baloo and Mowgli together~Bare Necessities walk~Kaa hypnosis scene~King Louie's ruined temple|classic songs~family adventure~strong character animation~easy charm|The Jungle Book is mostly song and character from the first few minutes on. Baloo, Kaa, and King Louie are the reasons people can still picture whole scenes.
1967|After Midnight|Belle de Jour|daytime visits to the salon~carriage fantasy images~fur coats and mirrored rooms~shifting line between routine and fantasy|cool surfaces~mysterious tone~provocative imagery~slow-burn effect|Belle de Jour keeps its distance in a way that makes the details sharper. The salon rooms and the fantasy flashes are what usually linger.

# 1968
1968|Crowd Favorite|2001: A Space Odyssey|Dawn of Man opening~space station docking~HAL's calm voice in the pod bay~stargate color rush|monumental imagery~mysterious tone~technical beauty~big-screen immersion|2001 is remembered in chunks: the bone, the docking ballet, HAL's voice, and that color tunnel. The movie feels less like a plot than a series of giant images hanging in space.
1968|After Midnight|Rosemary's Baby|new apartment tour~neighbors crossing the hallway~dreamlike party and ritual images~street-level panic in Manhattan|urban paranoia~quiet dread~psychological unease~slow-burn control|Rosemary's Baby takes ordinary apartment living and turns it sour one visitor at a time. The hallway, the old building, and those bad-dream images are what keep returning.
1968|Big Screen Moment|Planet of the Apes|astronauts landing in the wasteland~first sight of the ape society~human hunt through the cornfield~tribunal in the ape city|high-concept spectacle~memorable makeup~adventure momentum~big idea energy|The first reveal of the ape society is the hook, and the chase through the cornfield hits right after. Planet of the Apes still has the charge of a giant idea arriving fully formed.
1968|Rewatchable|Bullitt|airport surveillance~mustang chase through San Francisco~quiet apartment scenes~hospital corridor pressure|cool restraint~great car action~city atmosphere~strong star presence|The car chase is why Bullitt comes up first, but the silences around Steve McQueen are what give the movie its flavor. San Francisco feels like part of the machinery.
1968|Cult Favorite|Night of the Living Dead|graveyard attack~boarding up the farmhouse~television reports in the house~firelit mobs outside|raw horror energy~siege tension~bleak mood~indie grit|Night of the Living Dead is remembered through the farmhouse windows and the sound of bad news coming from a TV set. The rough edges are part of why it still lands.
1968|Date Night|Funny Girl|People number onstage~roller-skate routine~train station goodbye~theater rehearsals and backstage rush|show-business sparkle~star charisma~big songs~romantic yearning|Funny Girl has the big stage numbers people expect, but the train station emotion is just as important to the memory. Barbra Streisand gives the whole film its shine.
1968|Underrated|The Odd Couple|sloppy apartment first reveal~poker-night chaos~double-date dinner~Oscar and Felix circling the same argument again|great comic pairing~apartment comedy~dialogue snap~domestic absurdity|The Odd Couple is basically an apartment full of little disasters, which is exactly why it holds up. Matthau and Lemmon never let the mismatch get old.
1968|The One That Grows on You|Romeo and Juliet|masked party meeting~balcony scene~church wedding hush~dawn breaking after the night together|young intensity~lush period feeling~famous romance~sincere emotion|Romeo and Juliet keeps returning through faces, costumes, and candlelight more than speeches. The party and the balcony are the images nearly everybody starts with.
1968|Crowd Favorite|Oliver!|Consider Yourself number~Food Glorious Food in the hall~Who Will Buy at sunrise~street crowd dancing through London|big musical energy~crowd scenes~family appeal~memorable songs|Oliver! is all motion and song from the first big group number on. The crowds and market scenes give the whole movie its bounce.
1968|After Midnight|Once Upon a Time in the West|opening station wait~harmonica introduction~Jill arriving at the ranch~dusty town standoffs|patient tension~western atmosphere~mythic scale~music that lingers|That opening at the station tells you exactly how patient the movie plans to be. Once Upon a Time in the West keeps letting the silence and the landscape do the talking.

# 1970
1970|Crowd Favorite|Airport|stormy runway pressure~crowded terminal scenes~bomb threat spreading quietly~landing attempt everyone waits on|disaster-movie setup~ensemble tension~busy atmosphere~crowd appeal|Airport remembers the terminal, the storm, and the way every conversation feels like it might matter. The movie has the all-star disaster formula locked in early.
1970|After Midnight|Five Easy Pieces|piano at the truck stop~roadside diner argument~oil-field homecoming~quiet scenes between siblings|restless character study~great performance~drifting mood~plainspoken sadness|Five Easy Pieces hangs on Jack Nicholson in small rooms and ugly silences. The diner scene is famous for a reason, but the road drifting is what stays behind.
1970|Big Screen Moment|Patton|speech in front of the giant flag~tanks moving across the desert~war-room strategy maps~battlefield viewed from high ground|commanding performance~historical scale~military pageantry~big-screen presence|That speech in front of the flag gets mentioned before anything else, and the tanks rolling out keep the size of the movie in place. George C. Scott gives Patton its whole center of gravity.
1970|Rewatchable|M*A*S*H|camp football buildup~operating room chaos~announcements over the loudspeaker~tent-life practical jokes|hangout ensemble~irreverent humor~anti-authority mood~loose rhythm|M*A*S*H feels like a camp full of people trying to entertain themselves one prank at a time. The loudspeaker jokes and football finish are what most people remember.
1970|Cult Favorite|Performance|rock-star hideout~identity games in the house~mirrors and makeup in every room~psychedelic montage turns|heady style~1960s residue~dangerous mood~cult strangeness|Performance spends so much time inside that strange house that the movie starts to feel sealed off from the world. The mirrors, music, and identity blur are why it keeps a cult following.
1970|Date Night|Love Story|ice-skating together~Harvard and Radcliffe courtship~snowy walks through campus~music theme carrying the mood|romantic sweep~tearjerker pull~famous score~young-lead chemistry|Love Story is remembered in scarves, snow, and two people talking their way toward trouble. The score does a lot of the emotional lifting, and people still know it on the spot.
1970|Underrated|Little Big Man|frontier travel with different identities~old Chief Dan George scenes~battlefield seen from the margins~Dustin Hoffman aging through the years|wide-ranging tone~revisionist western feel~strong character thread~dark humor|Little Big Man moves through the West like it keeps changing masks every few scenes. Chief Dan George and Hoffman's shapeshifting give the picture its personality.
1970|The One That Grows on You|The Conformist|blue nighttime streets~government office routines~car ride through the forest~dance floor under the hanging lights|political chill~gorgeous cinematography~moral unease~slow-burn pull|The Conformist comes back through color and movement before anything else. Those forests, hallways, and dance scenes keep looking more precise with time.
1970|Crowd Favorite|Kelly's Heroes|tank crew on the road~oddball unit meeting up~bridge and village battle~Donald Sutherland's entrance as Oddball|war-movie fun~comic chemistry~mission momentum~favorite-character appeal|Kelly's Heroes is mostly remembered through the tank crew and Donald Sutherland drifting in from another movie entirely. The mission gives everybody just enough to do.
1970|After Midnight|Woodstock|helicopter views of the crowd~rain and mud everywhere~nighttime stage lights~performers talking to the audience between songs|concert immersion~era snapshot~collective feeling~music-first energy|Woodstock is about the crowd almost as much as the performers, especially once the mud and sheer size take over. The movie plays like a memory bank for one long weekend.

# 1971
1971|Crowd Favorite|The French Connection|subway pursuit~car chase under the tracks~stakeout in the cold~Popeye Doyle chasing the lead|gritty energy~street-level realism~great chase work~restless pace|The chase under the elevated tracks is the first thing out of almost everybody's mouth. The French Connection keeps that same rough street energy in nearly every scene.
1971|After Midnight|The Last Picture Show|small-town movie house~pool hall and cafe scenes~windy football field emptiness~awkward visits that keep turning sad|fading-town mood~strong ensemble~quiet heartbreak~black-and-white texture|The Last Picture Show feels like a town trying to remember itself while it is already slipping away. The diner, the theater, and the empty streets do most of the talking.
1971|Big Screen Moment|Diamonds Are Forever|Las Vegas casino floor~moon buggy escape~elevator fight~oil rig finish setup|glossy Bond fun~Vegas spectacle~light touch~set-piece appeal|Diamonds Are Forever remembers Vegas first and espionage second, which is part of the charm. The moon buggy and the casino mood are what people carry away.
1971|Rewatchable|Willy Wonka & the Chocolate Factory|golden ticket rush~factory gates opening~boat tunnel ride~glass elevator launch|pure imagination~family adventure~eccentric humor~memorable visuals|The factory opening is one of those scenes that lives permanently in movie memory. Willy Wonka also has the tunnel ride and Gene Wilder's entrance working in its favor.
1971|Cult Favorite|A Clockwork Orange|Korova Milk Bar opening~slow-motion home invasion style~record-shop wanderings~Ludovico treatment scenes|provocative style~disturbing satire~bold imagery~unsettling tone|A Clockwork Orange is remembered through costume, music, and a grin that never means anything good. Kubrick keeps every scene a little too clean, which makes the whole thing stranger.
1971|Date Night|Fiddler on the Roof|Tradition in the village~matchmaker scenes~sunset wedding dance~To Life in the tavern|famous songs~community feeling~family emotion~old-world atmosphere|Fiddler on the Roof is remembered through the songs and the village routines that surround them. Tevye talking to the sky gives the movie its whole tone.
1971|Underrated|Klute|missing-person investigation~Bree's taped sessions~phone calls in the apartment~rainy city walks|urban paranoia~performance focus~detective undercurrent~1970s texture|Klute lets the detective story sit behind Jane Fonda's performance instead of in front of it. The city, the phone calls, and the taped sessions are what last.
1971|The One That Grows on You|McCabe & Mrs. Miller|snowy frontier town opening~gambling house and baths~Leonard Cohen songs over the drift~business talks turning dangerous|dreamy western mood~muddy realism~musical atmosphere~slow pull|McCabe & Mrs. Miller looks half buried in snow and smoke from the first frames on. The town itself becomes the reason the movie sticks.
1971|Crowd Favorite|Dirty Harry|rooftop sniper scene~stadium ransom drop~school bus taken on the road~Harry and the .44 in open daylight|cop-thriller tension~tough-guy appeal~famous one-liners~lean pacing|Dirty Harry comes down to set pieces and attitude, and it has plenty of both. The rooftop and the stadium are the moments people usually go to first.
1971|After Midnight|Harold and Maude|funeral pranks~tree transplanting by night~train-yard outings~the little yellow car on the road|offbeat romance~dark humor~gentle rebellion~strange sweetness|Harold and Maude turns funerals and stolen afternoons into a whole way of looking at the world. The movie stays unusual without getting cold.

# 1972
1972|Crowd Favorite|The Godfather|wedding day introductions~restaurant meeting in the Bronx~horse head shock~family business at the compound|iconic scenes~family power drama~memorable performances~endless rewatch talk|The wedding, the restaurant, and that horse-head shock are enough to make The Godfather instantly recognizable. Every room in the movie feels important the second somebody walks into it.
1972|After Midnight|Cabaret|Willkommen opening~Liza Minnelli onstage~beer garden crowd turning the song~backstage and bedroom life crossing|show-business electricity~political shadow~performance-centered~bold style|Cabaret keeps moving between the stage and the world outside until the difference starts to disappear. Liza Minnelli owns every number, which is most of the memory right there.
1972|Big Screen Moment|The Poseidon Adventure|ballroom ceiling turning over~climbing toward the hull~flooding corridors~group trying another impossible route|disaster-movie scale~physical suspense~ensemble peril~set-piece momentum|The overturned ballroom is the image nearly everybody carries away. The Poseidon Adventure never stops making its group climb through another bad idea.
1972|Rewatchable|Sleuth|mansion game between two men~mechanical toys everywhere~role-playing tricks~another round of deception in the house|actor showcase~fun puzzle energy~single-location tension~wicked humor|Sleuth is mostly two men in a house trying to outperform each other, and that is more than enough. The toys and the traps make the place feel like part of the duel.
1972|Cult Favorite|Pink Flamingos|opening in the trailer~chaotic errands around town~rivals plotting in ugly rooms~Divine turning every scene into a dare|transgressive attitude~underground energy~camp shock~pure cult appeal|Pink Flamingos built its reputation on audacity, and the movie never softens that for a second. Divine's presence is the whole point.
1972|Date Night|What's Up, Doc?|hotel-lobby confusion~bags getting switched~banter on the stairs~San Francisco car chase comedy|screwball bounce~comic chemistry~city fun~fast joke pace|What's Up, Doc? keeps throwing another mix-up into the pile until the whole movie is running downhill. Barbra Streisand and Ryan O'Neal give it the exact right speed.
1972|Underrated|Sounder|rural family routines~children walking the fields~courtroom trip to town~the dog returning home battered|quiet dignity~family feeling~rural atmosphere~emotional restraint|Sounder stays with people because it never pushes harder than it needs to. The farm, the walks, and the dog's return carry a lot of feeling on their own.
1972|The One That Grows on You|Solaris|space station arrival~hallway drifting in silence~memories appearing in the cabin~library room in zero gravity|philosophical mood~haunting imagery~slow immersion~emotional mystery|Solaris asks for patience, then starts paying it back in long quiet stretches and odd emotional echoes. The station feels lonely in a way that gets stronger later.
1972|Crowd Favorite|Deliverance|dueling banjos~river rapids journey~mountain men watching from a distance~canoes sliding into worse country|backwoods tension~survival momentum~outdoor danger~scenes people quote|The banjo scene made Deliverance famous, but the river trip and the feeling of going too far are what really stay. The movie does not need much more than landscape and nerves.
1972|After Midnight|Last Tango in Paris|empty apartment meetings~Paris street wandering~costume-ball chaos~riverbank and bridge moments|raw intimacy~adult unease~strong atmosphere~unpredictable mood|Last Tango in Paris is remembered through the apartment and the discomfort it creates around every meeting. The film has a bruised, unstable feeling that keeps it in late-night conversation.

# 1973
1973|Crowd Favorite|The Sting|card game con at the train car~back-room setup with the gang~fake betting parlor~ragtime score over every move|slick fun~great chemistry~twisty caper feel~period charm|The Sting is basically a string of setups people love watching click into place. Paul Newman and Robert Redford make the whole thing glide.
1973|After Midnight|The Exorcist|bedroom noises in the dark~hospital test sequence~Father Karras hearing the case~stairs outside the Georgetown house|intense dread~shock scenes~serious tone~lasting creepiness|The bedroom, the tests, and those exterior stairs are enough to bring The Exorcist back instantly. The movie takes its horror seriously, which is part of why it still rattles people.
1973|Big Screen Moment|Enter the Dragon|mirror room setup~island tournament fights~nunchaku training~boat ride into Han's fortress|martial-arts showcase~star power~clean action~pure crowd energy|Enter the Dragon lives on through Bruce Lee's screen presence and that mirror room finish. Every fight is staged to make the audience sit up.
1973|Rewatchable|American Graffiti|cruising the strip at night~radio DJ floating over town~car challenge on the road~sock hop and school-night drifting|nostalgic soundtrack~hangout structure~youthful energy~car-culture appeal|American Graffiti is mostly headlights, radios, and people driving in circles because they are not ready to go home yet. The songs do a lot of the remembering for you.
1973|Cult Favorite|Don't Look Now|red coat in the crowd~Venice canals and alleys~church restoration work~little glimpses that may be nothing|moody unease~visual symbolism~grief underneath~slow-burn mystery|Don't Look Now uses Venice like the city is quietly closing around its characters. The red coat and the wet alleyways are what keep turning up in memory.
1973|Date Night|The Way We Were|first campus arguments~reunion after years apart~car ride and conversation in the dark~street meeting with the old song returning|romantic melancholy~star chemistry~famous theme~sweeping feeling|The Way We Were is remembered through the song, the faces, and the feeling that timing never lines up. Streisand and Redford make the whole picture easy to revisit.
1973|Underrated|Paper Moon|roadside hustle scenes~father-daughter bickering in the car~hotel-room scams~county-fair stretches|depression-era charm~comic timing~great pairing~black-and-white warmth|Paper Moon has the road-movie drift people like plus a father-daughter pairing that never settles into anything simple. The little scams are most of the fun.
1973|The One That Grows on You|Mean Streets|barroom introductions with rock music~pool-hall talk~church guilt hanging over Charlie~street fireworks and trouble|street-corner authenticity~music-driven feel~character-first energy~rough edges that help|Mean Streets remembers the bars, the streetlights, and Robert De Niro walking in like trouble already started. The movie keeps getting more alive with age.
1973|Crowd Favorite|Live and Let Die|boat chase through Louisiana~Tarot card meetings~double-decker bus pursuit~Bond entering Harlem under watch|Bond swagger~funky energy~big chases~memorable theme song|Live and Let Die has the boat chase, the song, and the changed-up Bond mood all working in its favor. It moves with more kick than polish, which helps.
1973|After Midnight|Serpico|undercover police work~wiry apartment life~appearing in disguise around the city~hearing room pressure|street realism~Al Pacino intensity~institutional mistrust~70s atmosphere|Serpico feels like New York grime caught in motion. Pacino's beard, disguises, and constant sense of not fitting in are the parts people keep picturing.

# 1974
1974|Crowd Favorite|Blazing Saddles|campfire beans scene~new sheriff arriving in town~fake frontier musical number~brawl spilling through different sets|big laugh moments~genre spoof fun~anarchic energy~endlessly quoted bits|Blazing Saddles is remembered scene by scene because the jokes come in giant chunks. The sheriff's arrival and the campfire sequence still get named first.
1974|After Midnight|Chinatown|water in the dry ditch~nose bandage after the alley beating~orange grove discoveries~Jake driving deeper into the mess|noir mystery~sunlit corruption~great performances~uneasy pull|The nose bandage alone is enough to pull Chinatown back into focus. The movie keeps finding uglier corners under bright California sunlight.
1974|Big Screen Moment|The Towering Inferno|party at the top of the skyscraper~fire spreading floor to floor~helicopter rescue gone wrong~glass elevator trapped high above the street|disaster spectacle~vertical tension~all-star cast~big-screen urgency|The glass, the height, and the fire are the whole memory of The Towering Inferno. The movie knows exactly how to use scale as pressure.
1974|Rewatchable|Young Frankenstein|putting on the Ritz number~monster first revealed in the lab~blind hermit scene~castle door gags and panic|comic performances~classic spoofing~great sight gags~rewatch comfort|Young Frankenstein has line readings and visual bits people can pull up from nowhere. Gene Wilder, Marty Feldman, and the monster make every return trip worth it.
1974|Cult Favorite|The Texas Chain Saw Massacre|van ride with bad vibes~first dinner at the house~Leatherface slamming the metal door~running through the dark woods|raw horror impact~documentary grime~nightmare imagery~relentless tension|The metal door slam is one of those horror moments people never lose. The Texas Chain Saw Massacre feels sweaty and immediate in a way polished horror usually does not.
1974|Date Night|The Great Gatsby|long island parties~yellow car on the road~Gatsby reaching toward the green light~quiet scenes across the bay|romantic melancholy~period glamour~star pairing~lush visuals|The parties and the green light do most of the work in memory. The Great Gatsby turns longing into something you can almost point at.
1974|Underrated|The Taking of Pelham One Two Three|subway hijack starts cold~dispatch room scrambling~mayor dragged into the mess~city trying to answer the ransom clock|city energy~smart tension~great dialogue~grimy humor|The Taking of Pelham One Two Three is mostly remembered through voices on radios and nerves in transit rooms. The New York feel is half the reason the movie lands.
1974|The One That Grows on You|The Conversation|Union Square surveillance job~wire recordings replayed in the workshop~raincoat and saxophone solitude~party where Harry loses control of the room|paranoid mood~sound design focus~lonely character study~slow pull|The Conversation keeps returning through tape reels, headphones, and Gene Hackman looking like he wishes he could disappear. The sound work is the movie's whole nervous system.
1974|Crowd Favorite|The Godfather Part II|young Vito in the old neighborhood~Lake Tahoe family gatherings~Cuba trip at New Year's~Michael alone in the compound|expansive scope~family power games~parallel storytelling~iconic atmosphere|The Godfather Part II keeps widening the family story without losing the heavy room-by-room feeling of the first movie. The Lake Tahoe and old-neighborhood sections are what many people picture first.
1974|After Midnight|Murder on the Orient Express|snowbound train stopped in the night~Poirot gathering everyone in one car~corridor comings and goings~lavish dining-car scenes|ensemble mystery fun~period detail~famous detective appeal~cozy tension|The train itself is the star as much as Poirot. Murder on the Orient Express feels like a box full of elegant suspects and small details.

# 1976
1976|Crowd Favorite|Rocky|meat locker workout~running through Philadelphia~Apollo publicity machine~training montage taking over the movie|underdog energy~memorable music~street-level heart~crowd-pleasing payoff|The run up the steps and the training montage are the images everybody shares, but the little Philadelphia details matter too. Rocky feels personal before it ever feels big.
1976|After Midnight|Taxi Driver|Travis driving through nighttime streets~mirror practice in the apartment~campaign office fixation~city seen through the windshield|urban alienation~dangerous mood~great central performance~haunting atmosphere|Taxi Driver is remembered through yellow cabs, red lights, and one apartment getting more claustrophobic by the minute. The city at night is half the movie.
1976|Big Screen Moment|King Kong|arrival on Skull Island~wall and ceremony reveal~Kong appearing from the jungle~climbing high above the city|giant-monster spectacle~adventure scale~famous iconography~big effects ambition|King Kong has the island buildup people want and the climb everybody already knows is coming. The sheer size of the creature is the whole point.
1976|Rewatchable|The Bad News Bears|little-league tryouts~beer-soaked dugout energy~training sessions with the team~final game chaos|sports-movie fun~rough-edged humor~kid-team appeal~easy rewatch pull|The Bad News Bears has the loose, nasty little-league tone that makes it stand apart from cleaner sports stories. Watching the team get slightly less awful is most of the fun.
1976|Cult Favorite|Carrie|high-school taunting in the locker room~bucket preparation above the stage~telekinesis flaring at home~prom floor turning into panic|horror with feeling~school-night cruelty~strong visual shock~outsider sympathy|Carrie is remembered through the prom almost automatically, but the locker room and the house matter just as much. The movie has hurt underneath the horror.
1976|Date Night|A Star Is Born|concert-stage introductions~backstage and hotel-room closeness~recording studio turns~audience lights washing over the stage|music-world romance~star chemistry~big feelings~show-business glamour|A Star Is Born remembers the stage lights and the backstage rooms right beside them. The romance is huge and messy in exactly the way people expect.
1976|Underrated|Marathon Man|dentist chair terror~diamonds changing hands~city running scenes~safe room that never feels safe|paranoia thriller~nerve-shredding set pieces~great villain~70s grit|The dentist scene is the first thing people bring up, and Marathon Man earns that reputation. The whole movie feels like New York got turned into a trap.
1976|The One That Grows on You|All the President's Men|newsroom verification work~parking-garage meetings~phone calls that keep stalling out~typewriters and fluorescent offices|process detail~quiet suspense~journalism focus~steady momentum|All the President's Men gets stronger once the phone calls and checking become the real action. The newsroom glow and the garage meetings are the lasting images.
1976|Crowd Favorite|The Omen|birthday-party accident~nanny on the roof~church scenes that feel all wrong~road trip to learn more|creepy atmosphere~memorable shocks~ominous score~horror-pop appeal|The Omen made its name on a few hard jolts, and the birthday party is near the top of the list. The movie keeps a cloud over everything from the first family scenes on.
1976|After Midnight|Network|mad-as-hell speech~television studio frenzy~conference-room deals~on-air personalities becoming product|biting satire~famous speeches~performance fireworks~still-relevant anger|Network is remembered through speeches first, especially when Peter Finch turns the whole studio into a pressure valve. The boardroom scenes are nearly as sharp.

# 1977
1977|Crowd Favorite|Star Wars|cantina on Tatooine~Millennium Falcon escape~Death Star trench run~binary sunset with the score rising|mythic adventure~instantly recognizable images~pure movie momentum~crowd reaction fuel|Star Wars has too many iconic images to count, but the cantina, the Falcon, and the trench run are near the top. The movie moves with total confidence once it gets going.
1977|After Midnight|Annie Hall|balcony and movie-line talk~split-screen conversation~lobster scene in the kitchen~Alvy and Annie in the city together|modern relationship comedy~nervy humor~New York feeling~sharp writing|Annie Hall remembers itself through conversation bits people can almost hear again. The movie keeps the romance light and the regret close by.
1977|Big Screen Moment|Close Encounters of the Third Kind|nighttime road encounter~Barry and the kitchen lights~Devils Tower shaped in mashed potatoes~mothership arrival at the landing site|awe on a big scale~sound-and-light spectacle~everyday wonder~Spielberg sincerity|The kitchen lights, Devils Tower, and the final arrival make Close Encounters feel bigger every time it comes up. Spielberg sells amazement without forcing it.
1977|Rewatchable|Smokey and the Bandit|Trans Am launching out of the start~CB chatter across the highway~Buford T. Justice on the chase~roadside flirting between stops|road-movie fun~easy star chemistry~southern humor~high-speed charm|Smokey and the Bandit is mostly remembered as motion and attitude from one highway to the next. The CB chatter and Jackie Gleason's pursuit keep the whole thing loose.
1977|Cult Favorite|Suspiria|dance-school arrival in the rain~colored hallways glowing at night~academy staircases and secret corridors~practice rooms turning uncanny|dream-horror style~wild color design~music that drills in~nightmare mood|Suspiria announces itself with rain and color before it has to do anything else. The school corridors and Goblin score are enough to keep it alive in memory.
1977|Date Night|The Goodbye Girl|awkward move-in arrangement~Broadway rehearsal scenes~single-parent household rhythms~dancing around real feelings|romantic-comedy warmth~New York apartment life~strong performances~gentle humor|The Goodbye Girl remembers the apartment and the performances inside it more than any big plot turn. Richard Dreyfuss and Marsha Mason keep the movie grounded and warm.
1977|Underrated|Sorcerer|bridge crossing with the trucks~sweat-soaked jungle roads~nitroglycerin delivery plan~men forced into the same bad mission|physical suspense~bleak adventure~great atmosphere~serious tension|Sorcerer is the truck-on-the-bridge movie for a reason, but the jungle misery around that sequence matters too. The whole picture feels dangerous in a very material way.
1977|The One That Grows on You|Eraserhead|industrial landscape opening~awkward dinner with the family~tiny apartment and radiator fantasy~night sounds that never stop|surreal nightmare~industrial dread~strange humor~images that burrow in|Eraserhead is all texture: pipes, shadows, and noises that sound wrong in the middle of the night. The dinner and the apartment are the pieces that keep resurfacing.
1977|Crowd Favorite|Saturday Night Fever|paint store by day~walking Brooklyn with the strut~dance-floor spotlight~car ride over the bridge at night|great soundtrack~dance appeal~urban energy~star-making role|The white suit and the dance floor are what everybody thinks of first, but the late-night drives matter too. Saturday Night Fever has a strong feel for its streets.
1977|After Midnight|The Spy Who Loved Me|ski jump opening~underwater Lotus reveal~Egyptian ruins chase~Bond and Anya in the desert|big Bond spectacle~globe-trotting fun~memorable gadgets~clean action|The ski jump and the underwater car are enough to carry the memory of The Spy Who Loved Me all by themselves. The movie is pure large-scale Bond pleasure.

# 1979
1979|Crowd Favorite|Alien|awakening on the Nostromo~facehugger in the med bay~ventilation shafts search~crew eating together before disaster|industrial sci-fi mood~perfect creature design~siege tension~images that never fade|Alien remembers the ship almost like a bad workplace, then the creature turns every corridor into danger. The med bay and the vents are the moments people always name.
1979|After Midnight|Apocalypse Now|helicopters over the surf~river patrol drifting deeper~USO show on the stage~temple shadows near the end of the trip|war-movie hallucination~huge sound design~unsettling grandeur~journey into darkness|The helicopters and the river are the two big pieces that keep Apocalypse Now alive in memory. The movie feels like it is pulling the boat farther away from ordinary reality the whole time.
1979|Big Screen Moment|Star Trek: The Motion Picture|Klingon attack opening~slow reveal of the refitted Enterprise~V'Ger cloud stretching across space~spacesuit journey into the light|cosmic scale~big visual ambition~franchise nostalgia~awe-driven pacing|The long Enterprise reveal is half the reason Star Trek: The Motion Picture exists, and fans still remember every second of it. The V'Ger imagery goes for full cosmic wonder.
1979|Rewatchable|The Muppet Movie|opening in the swamp~Kermit on the bicycle~road trip with the whole gang~big Hollywood finale mood|family fun~road-movie charm~playful songs~character chemistry|The Muppet Movie is easy to revisit because the road trip keeps handing you another familiar face. Kermit on the bike and Rainbow Connection do most of the heavy lifting.
1979|Cult Favorite|Mad Max|Main Force Patrol on the highways~Toecutter and the gang riding in~night roads with flashing lights~interceptor roaring through the wasteland|punk road energy~stripped-down action~feral atmosphere~cult attitude|Mad Max feels fast and sunburned from the first highway run. The patrol cars, leather, and screaming engines are the whole memory.
1979|Date Night|Manhattan|black-and-white skyline opening~museum and restaurant dates~bench by the river at dawn~city streets under Gershwin|romantic urban mood~great opening imagery~conversation-driven~New York glow|Manhattan starts by putting the skyline on a pedestal and never really steps down from it. The museums, restaurants, and river bench are what people hold onto.
1979|Underrated|The China Syndrome|nuclear-plant control room~television-news scrambling~corporate pressure behind closed doors~roadside confrontation in daylight|procedural tension~topical anxiety~strong cast~80s-before-the-80s feel|The China Syndrome gets a lot of mileage out of control-room procedure and the dread hiding inside it. Jane Fonda and Jack Lemmon keep the whole thing urgent.
1979|The One That Grows on You|Being There|Chance in the garden~television shaping his speech~walks through Washington rooms~people hearing more than he says|deadpan satire~simple surfaces~quiet humor~odd warmth|Being There looks almost too simple at first, and that is part of the trick. Peter Sellers lets small pauses do most of the work.
1979|Crowd Favorite|Kramer vs. Kramer|morning routine in the apartment~parenting getting learned on the fly~courtroom testimony~father and son crossing the city together|emotional directness~strong performances~family focus~ordinary-life detail|Kramer vs. Kramer is remembered through kitchens, classrooms, and adults trying to keep composure in public. The apartment scenes give the story most of its weight.
1979|After Midnight|All That Jazz|opening audition sequence~surgical visions and fantasy stage turns~editing room stress~backstage mirror rituals|show-business exhaustion~dazzling numbers~dark humor~autobiographical heat|All That Jazz keeps turning work, illness, and fantasy into the same feverish rhythm. The opening audition and all those mirror scenes stay vivid.

# 1980
1980|Crowd Favorite|The Empire Strikes Back|Hoth battle~Yoda in the swamp~asteroid field chase~Cloud City corridors|beloved sequel energy~darker tone~favorite characters~huge adventure pull|The Empire Strikes Back has the walkers on Hoth, Yoda in the swamp, and the asteroid field all in one run. A lot of people still call it the high point because every setting is memorable.
1980|After Midnight|Raging Bull|ring sequences in black and white~training and weight cutting~nightclub routines~LaMotta alone with the mirror|brutal intensity~great performance~stylized violence~self-destruction on display|Raging Bull remembers the ring first, but the dressing-room and nightclub scenes cut just as deep. The movie is all force and damage.
1980|Big Screen Moment|Superman II|three villains arriving on Earth~Metropolis fight in the streets~Niagara Falls rescue~Fortress of Solitude showdown|comic-book spectacle~heroic fun~big action scenes~crowd appeal|Superman II is the one people remember for the villains really pushing Superman around in public. Metropolis getting turned inside out is the hook.
1980|Rewatchable|Airplane!|nervous passenger setup~autopilot gag~flashbacks and overreactions~landing chaos with everybody shouting|rapid-fire jokes~endless quotables~silly confidence~great replay value|Airplane! is basically wall-to-wall bits, and a lot of them still land on sight. The cockpit panic and all those dead-serious line readings keep it moving.
1980|Cult Favorite|The Shining|hotel tour on arrival~big wheel through the empty halls~ballroom and Gold Room visions~hedge maze outside in the cold|creeping dread~iconic imagery~labyrinthine setting~slow-burn horror|The Overlook Hotel is the memory more than any one scare. The carpet, the tricycle, and those huge empty rooms make The Shining hard to shake.
1980|Date Night|Fame|auditions at the school~street dance energy~rehearsal room frustrations~title number spilling out into traffic|showbiz drive~ensemble energy~youthful ambition~music and dance pull|Fame is remembered through auditions, practice rooms, and that title number taking over the street. The movie has so much youthful push that it almost runs on adrenaline.
1980|Underrated|The Elephant Man|factory smoke and opening dread~hospital demonstrations~quiet scenes with books and respect~theater-night acceptance|deep sympathy~beautiful black-and-white~careful performances~human dignity|The Elephant Man is remembered through John Hurt's face and the gentleness built around it. The hospital rooms and the theater night are the scenes that stay with people.
1980|The One That Grows on You|Ordinary People|therapy sessions~lake memory hanging over everything~kitchen arguments~family trying to sit at the same table|emotional honesty~suburban tension~quiet performances~pain beneath routine|Ordinary People gets heavier later because the drama is so close to everyday life. The therapy rooms and family meals are where the movie really lives.
1980|Crowd Favorite|Caddyshack|pool chaos at the club~Bill Murray with the gopher~baby ruth bar moment~final tournament meltdown|loose comedy energy~favorite character bits~summer-movie feel~rewatch comfort|Caddyshack survives almost entirely on scene memory, and that is enough. The gopher, the pool, and the tournament are the pieces everyone knows.
1980|After Midnight|Friday the 13th|Camp Crystal Lake reopening~storm moving in~cabin-by-cabin unease~lake and woods at night|slasher simplicity~camp setting~creeping suspense~franchise kick-off feel|Friday the 13th made the summer camp look like a terrible place to spend the weekend. The storm, the cabins, and the dark lake are the basic memory set.

# 1981
1981|Crowd Favorite|Raiders of the Lost Ark|boulder opening escape~truck chase in the desert~map room reveal~marketplace pursuit|pure adventure fun~iconic hero~great set pieces~old-serial momentum|Raiders of the Lost Ark hits the boulder, the marketplace, and the truck chase before most movies would be halfway done. Harrison Ford carries the whole thing like he was born there.
1981|After Midnight|Chariots of Fire|running on the beach~training with the score rising~Olympic buildup~quiet moments about belief and duty|uplifting music~measured emotion~sports-film grace~period atmosphere|The beach run with that score is what everybody remembers first, and Chariots of Fire earns it. The movie keeps its dignity without turning stiff.
1981|Big Screen Moment|Excalibur|sword in the stone imagery~knights riding through silver forests~battle in bright armor~round table at full splendor|mythic scale~shiny visual style~fantasy grandeur~sincere heroic tone|Excalibur goes for myth in every frame, from the armor to the forests to the mist. The movie looks huge even when it is only showing a handful of riders.
1981|Rewatchable|Arthur|drunken one-liners~department-store date~chauffeur Hobson stealing scenes~public singing and chaos|star charisma~comic timing~surprisingly sweet core~easy replay value|Arthur is mostly a performance machine for Dudley Moore and John Gielgud, and that is enough. The jokes come easy, but the warmth is why people come back.
1981|Cult Favorite|An American Werewolf in London|moors attack in the dark~hospital recovery and bad dreams~subway stalking sequence~Piccadilly Circus panic|horror-comedy balance~great transformation work~urban nightmare feel~cult charm|The werewolf transformation is the image people bring up first, but the subway sequence is right there with it. The movie finds a rare balance between laughs and dread.
1981|Date Night|On Golden Pond|summer-house arrival~father and daughter circling old grievances~loon calls on the lake~quiet mornings by the water|gentle emotion~lakehouse atmosphere~great performances~family warmth|On Golden Pond is remembered through the lake, the house, and conversations that sound like years are packed inside them. The whole picture has late-summer feeling.
1981|Underrated|Blow Out|sound recording on the bridge~film and tape being matched together~parade chaos growing dangerous~Philadelphia moving under neon and rain|great craft tension~political paranoia~audio-driven suspense~stylish grit|Blow Out makes microphones and tape reels feel like action tools. The bridge recording and the parade are the scenes people can see and hear again.
1981|The One That Grows on You|Body Heat|humid Florida nights~porch fan spinning in the dark~courtroom and legal pressure~desire turning into a trap|sweaty noir mood~adult tension~sultry atmosphere~slow-burn menace|Body Heat runs on humidity, porch lights, and people making very bad decisions in slow motion. The whole movie seems warm enough to melt.
1981|Crowd Favorite|The Road Warrior|opening road narration~vehicular ambushes in the dust~compound under siege~long tanker chase|lean action~post-apocalyptic cool~amazing stunt work~cult and crowd appeal|The tanker chase alone would have been enough to keep The Road Warrior alive. Everything around it is stripped down to speed, dust, and movement.
1981|After Midnight|Time Bandits|bedroom closet gateway~historical leaps through different eras~giant's head in the horizon~labyrinth of maps and time holes|imaginative fantasy~oddball humor~visual invention~dream-logic appeal|Time Bandits feels like a child rummaging through history with a flashlight. The map, the bedroom, and all the sudden era changes are why people remember it so clearly.

# 1983
1983|Crowd Favorite|Return of the Jedi|Jabba's palace rescue~speeder bikes through the forest~Emperor's throne room setup~space battle above Endor|space-opera payoff~favorite characters~big action scenes~fan-service pleasure|Return of the Jedi remembers itself through Jabba's palace, the speeder bikes, and everything happening over Endor at once. It plays like a victory lap with enough scale to earn it.
1983|After Midnight|Terms of Endearment|mother-daughter phone calls~hospital scenes growing heavier~dating life turning messy~neighbors and family all crowding in|big feelings~great performances~humor beside sadness~family drama pull|Terms of Endearment keeps switching from jokes to hurt in a way people still remember. Shirley MacLaine and Debra Winger make every scene feel lived in.
1983|Big Screen Moment|Scarface|nightclub rise in Miami~chainsaw sequence shock~Tony building his empire~mansion excess growing louder|operatic crime scale~huge central performance~neon style~memorable attitude|Scarface is remembered in chunks of excess: the club, the mansion, the mountains of bad choices. Al Pacino pushes every scene hard enough that it sticks.
1983|Rewatchable|Trading Places|commodities-floor chaos~Santa suit on the train~Dan Aykroyd in bad disguise~party and bet setup|comic chemistry~holiday feel~sharp social comedy~favorite bits everywhere|Trading Places gives Eddie Murphy and Dan Aykroyd a setup strong enough to carry scene after scene. The train and the trading floor are where most memories land.
1983|Cult Favorite|Christine|car restoration montage~showroom-red bodywork gleaming~bully confrontations after dark~street pursuit with the headlights coming on|killer-car concept~1950s nostalgia twisted~synth-and-rock mood~cult fun|Christine makes a car feel vain, angry, and weirdly elegant all at once. The restoration scenes and those headlights in the dark are what people keep picturing.
1983|Date Night|Flashdance|warehouse loft and welding~dance-school audition hopes~water splash club scene~final audition routine|music-video energy~dance appeal~romantic pull~1980s style blast|Flashdance is remembered through pure image: the loft, the chair-and-water scene, and that final audition. The movie runs on rhythm more than plot.
1983|Underrated|The Right Stuff|test pilots swapping stories~aircraft breaking apart in the sky~Mercury capsule launches~families watching from home|aviation awe~ensemble storytelling~American mythmaking~solid humor|The Right Stuff remembers itself through launch pads, speed records, and big personalities trying to top each other. The movie has plenty of size without losing its grin.
1983|The One That Grows on You|The Outsiders|sunset talks between the boys~drive-in double date~rumble preparations~church hideout in the country|young-cast sincerity~outsider feeling~small-town mood~softness under the toughness|The Outsiders tends to stick through faces, leather jackets, and sunset conversation more than the fights. The movie has more tenderness than its reputation suggests.
1983|Crowd Favorite|National Lampoon's Vacation|family loading the wagon~roadside disasters piling up~Wally World obsession growing bigger~strange detours across the country|road-trip comedy~favorite set pieces~family chaos~rewatch comfort|Vacation is remembered scene by scene because the trip keeps going wrong in new ways. The wagon and the dream of Wally World carry the whole movie.
1983|After Midnight|WarGames|bedroom computer dialing out~NORAD screens lighting up~simulation blurring into panic~arcade and mountain-facility vibes|tech paranoia~teen hero appeal~cold-war suspense~smart concept|WarGames made a bedroom computer feel like a live wire. The blinking screens, the phone line connections, and the bunker atmosphere are what stay in people's heads.

# 1986
1986|Crowd Favorite|Top Gun|opening launch sequence on the carrier~bar singalong~volleyball on the beach~dogfight training runs|star charisma~jet-fueled spectacle~great soundtrack~instant-movie-star energy|Top Gun is remembered through jets, sunglasses, and music almost as much as dialogue. The carrier opening and the dogfights are pure movie memory.
1986|After Midnight|Platoon|helicopters over the tree line~night ambush in the jungle~bunker arguments between sergeants~soldiers moving through smoke at dawn|war-zone immediacy~moral conflict~intense atmosphere~strong ensemble|Platoon feels close to the ground in a way most war movies do not. The night ambush and the tension inside the platoon are what people tend to remember first.
1986|Big Screen Moment|Aliens|drop-ship arrival on the colony~motion tracker in the corridor~Ripley loading up~power-loader showdown setup|crowd-thriller pace~great heroine~sci-fi action surge~memorable creature scares|Aliens gives you the colony, the tracker, and Ripley strapping in without wasting any time. The movie plays bigger and faster than most sequels dare to.
1986|Rewatchable|Ferris Bueller's Day Off|Ferris talking to camera~parade float in the city~borrowing the Ferrari~museum stop and downtown wandering|wish-fulfillment fun~comic timing~Chicago energy~favorite bits everywhere|Ferris Bueller's Day Off turns one skipped school day into a chain of scenes people still quote. The parade and the Ferrari are the obvious hooks, but Chicago gives the movie extra life.
1986|Cult Favorite|Blue Velvet|severed ear in the grass~nightclub with Isabella Rossellini singing~Frank Booth bursting into the room~suburban lawns hiding bad weather|dreamlike menace~surreal noir mood~strong imagery~cult fascination|Blue Velvet starts with a severed ear and never pretends suburbia is normal after that. The nightclub and Frank Booth are the pieces people can never quite shake.
1986|Date Night|Crocodile Dundee|first trip through New York~bar confrontations~outback stories told with a grin~walking the city as a novelty show|fish-out-of-water charm~easy star appeal~light romance~crowd-friendly humor|Crocodile Dundee is remembered for its one-liners and for how strange New York suddenly looks through Mick's eyes. The movie keeps the romance loose and friendly.
1986|Underrated|Stand by Me|walking the tracks~campfire stories at night~leech scene in the swamp~train bridge crossing|friendship focus~coming-of-age feeling~summer nostalgia~memorable set pieces|Stand by Me is all kids on the move with enough bad stories and summer air around them to make it stick. The bridge and the campfire are the scenes most people go back to.
1986|The One That Grows on You|Hannah and Her Sisters|holiday dinner tables~museum and bookstore wandering~apartment conversations~characters crossing in and out of each other's lives|ensemble warmth~talk-driven humor~New York intimacy~layered relationships|Hannah and Her Sisters gets richer once all the different apartments and conversations start connecting in memory. The holiday meals are the anchors.
1986|Crowd Favorite|Little Shop of Horrors|Skid Row opening number~Audrey II starting to sing~dentist office nightmare~shop filling up with success and trouble|musical-comedy fun~creature charm~big songs~cult and crowd appeal|Little Shop of Horrors has the plant, the songs, and a dentist scene nobody forgets. The movie is bright, nasty, and cheerful in the same breath.
1986|After Midnight|The Fly|teleportation pods introduced~lab experiment going wrong~body changes starting small~Jeff Goldblum growing wilder by the scene|body-horror intensity~tragic streak~great performance~gross-out effects that linger|The Fly gets remembered through the pods and the first little signs that something is very wrong. Jeff Goldblum makes the whole movie sadder than people expect.

# 1989
1989|Crowd Favorite|Batman|Batmobile reveal~museum vandalism with Prince on the soundtrack~cathedral climb at night~Batwing over the city skyline|comic-book spectacle~memorable villain~production design~pure event-movie pull|Batman is remembered through the Batmobile, the cathedral, and Jack Nicholson filling every room. The movie feels like Gotham got built inside a soundstage dream.
1989|After Midnight|Do the Right Thing|opening dance to Fight the Power~heat hanging over the block~pizza shop arguments~street corner turning louder by the hour|urgent energy~ensemble richness~neighborhood detail~social tension|Do the Right Thing keeps the whole block alive at once, which is why every storefront and sidewalk stays in memory. The heat and the music are part of the pressure.
1989|Big Screen Moment|Indiana Jones and the Last Crusade|young Indy on the train~Venice catacombs~tank battle across the desert~father and son riding into danger together|adventure scale~great chemistry~globe-trotting fun~crowd-pleasing action|The Last Crusade gets a lot of mileage out of Sean Connery and Harrison Ford arguing their way through danger. The tank battle and the Venice section are the highlights people usually name.
1989|Rewatchable|When Harry Met Sally...|road trip to New York~phone calls split across apartments~wagon wheel coffee talk~deli scene that everyone knows|rom-com gold standard~great dialogue~city comfort~lead chemistry|When Harry Met Sally... is remembered through conversations more than plot mechanics. The road trip, the phone calls, and the deli scene are enough to keep it in rotation.
1989|Cult Favorite|Heathers|croquet in bright blazers~cafeteria politics~notebook and fake-love-note plotting~darkly comic school corridors|acid teen satire~stylized attitude~dark humor~cult dialogue|Heathers turns high school into a poisonous popularity contest and never backs off the joke. The croquet sets, the colors, and the hallway talk are the pieces people carry around.
1989|Date Night|The Little Mermaid|Part of Your World on the rocks~Under the Sea sequence~boat ride on the lagoon~kiss-the-girl moonlight|classic Disney romance~great songs~family appeal~bright animation|The Little Mermaid is remembered in songs and moonlight almost immediately. Ariel on the rock and the lagoon boat ride are two of the biggest images Disney ever made.
1989|Underrated|Glory|training camp with the regiment~campfire singing and letters home~storming toward the fort~quiet looks before the fight|historical force~great ensemble~emotional weight~battlefield intensity|Glory remembers the training and the campfire songs just as much as the battlefield. The movie gives the regiment enough time together that the march into danger lands harder.
1989|The One That Grows on You|Field of Dreams|cornfield voices at dusk~diamond appearing in the field~road trip to Boston and beyond~night games under the lights|gentle fantasy~baseball mythology~father-son feeling~heartland atmosphere|Field of Dreams gets stronger later because the corn, the lights, and the strange quiet around the diamond feel so simple at first. The movie trusts those images enough to let them carry the feeling.
1989|Crowd Favorite|Dead Poets Society|Mr. Keating standing on the desk~cave meetings with the boys~classroom pages being torn out~students finding a new voice|inspirational charge~strong performances~school setting~memorable scenes|Dead Poets Society is remembered through a handful of classroom moments that people can picture instantly. Robin Williams gives the movie its beating heart.
1989|After Midnight|Sex, Lies, and Videotape|awkward living-room conversations~video camera interviews~hotel-bar unease~relationships turning under the same roof|talk-driven tension~indie-film intimacy~quiet discomfort~performance focus|Sex, Lies, and Videotape keeps the stakes inside apartments and conversations, which is why the discomfort feels so close. The camera interviews are the scenes most people remember.
"""

EXTRA_CATALOG_TEXT = """
# 2000
2000|Crowd Favorite|Gladiator|battle in Germania~first walk into the Colosseum~Maximus facing the crowd~sands of the arena kicking up everywhere|Roman spectacle~heroic momentum~crowd-pleasing action~memorable score|The Germania battle and the first walk into the Colosseum are what people usually picture first. Gladiator has dust, steel, and Russell Crowe staring down the whole arena.
2000|After Midnight|Crouching Tiger, Hidden Dragon|rooftop chase at night~bamboo forest duel~desert memories with Lo~stolen sword causing trouble everywhere|graceful action~romantic ache~sweeping beauty~legendary fight scenes|The rooftop chase and the bamboo fight still float back into memory with almost no effort. Crouching Tiger, Hidden Dragon moves like a dream and still lands every sword stroke.
2000|Big Screen Moment|X-Men|cage fight opening~first trip to Xavier's school~Magneto testing his machine~Statue of Liberty showdown|comic-book kickoff~ensemble appeal~mutant powers on display~franchise-start energy|The black leather, the school, and the Statue of Liberty finish are the parts most people grab first. X-Men has the feeling of a whole superhero lane opening up.
2000|Rewatchable|O Brother, Where Art Thou?|chain-gang escape in the field~recording in the radio station~river baptism stop~political rally with the song returning|quotable comedy~great soundtrack~road-movie charm~easy rewatch pull|The radio station scene and the song coming back later are enough to keep O Brother, Where Art Thou? in rotation. George Clooney and that whole wandering trio give the movie its bounce.
2000|Cult Favorite|Memento|Polaroids and notes in hand~backward scene structure clicking into place~tattoos guiding the next move~motel-room confusion all over again|brain-teaser appeal~neo-noir mood~structural hook~cult rewatch culture|Memento is remembered through Polaroids, tattoos, and the strange feeling of always arriving in the middle. The backward structure keeps the whole thing alive in conversation.
2000|Date Night|Chocolat|small-town chocolate shop opening~market-day glances~river people arriving with a different energy~windows filling with sweets|romantic warmth~cozy atmosphere~period charm~comfort-movie feel|Chocolat is mostly memory by texture: shop windows, melted chocolate, and Juliette Binoche changing the mood of the town. The whole movie feels like cold weather giving way.
2000|Underrated|Erin Brockovich|file boxes stacking up on the table~Erin knocking on doors in the heat~water samples raising questions~office finally understanding what she has|star performance~real-world stakes~blue-collar grit~straight-ahead momentum|The door-knocking and the file work are just as memorable as the attitude Julia Roberts brings into every room. Erin Brockovich keeps the pressure tied to ordinary people.
2000|The One That Grows on You|Almost Famous|bus rides with the band~Tiny Dancer singalong~backstage drift before the show~William taking notes while everything gets messy|music-world nostalgia~coming-of-age pull~hangout rhythm~big heart|Almost Famous gets stronger later because the bus rides and backstage moments feel lived in instead of arranged. The Tiny Dancer scene still does most of the talking.
2000|Crowd Favorite|Cast Away|plane crash aftermath~fire finally catching~Wilson on the raft~return to the world after years away|survival hook~island imagery~solo-star showcase~emotional directness|The crash, the volleyball, and that stretch on the raft are the pieces nearly everybody remembers. Cast Away keeps the screen company with Tom Hanks and a lot of empty horizon.
2000|After Midnight|Traffic|border crossings and handoffs~judge's daughter slipping away at night~Washington strategy rooms~multiple stories tightening together|layered storytelling~drug-war tension~ensemble reach~restless style|Traffic keeps cutting between rooms, cities, and points of view until the whole thing feels like one connected headache. The structure is the memory almost as much as any one scene.

# 2001
2001|Crowd Favorite|The Lord of the Rings: The Fellowship of the Ring|Shire opening with Bilbo's party~Moria under the mountain~bridge in Khazad-dum~Argonath towering over the river|epic world-building~adventure pull~beloved ensemble~big-screen fantasy|The Shire, Moria, and that river run past the giant statues are enough to bring Fellowship right back. The movie opens a whole world and makes every stop feel worth lingering on.
2001|After Midnight|Mulholland Drive|car stopping on the dark road~audition turning the room quiet~Club Silencio~Hollywood apartments full of doubles and echoes|dream logic~mystery mood~haunting imagery~late-night pull|Mulholland Drive sticks through isolated moments more than explanations: the road at night, the audition, the stage at Club Silencio. The whole movie feels like Los Angeles after the lights go strange.
2001|Big Screen Moment|Harry Potter and the Sorcerer's Stone|letters flooding the house~first walk through Diagon Alley~sorting hat ceremony~chessboard challenge under the school|wizarding-world wonder~family event feel~iconic locations~series-launch excitement|Diagon Alley and the Great Hall do most of the work the first time around, and those images have never really faded. Harry Potter and the Sorcerer's Stone sells the fun of simply getting through the door.
2001|Rewatchable|Ocean's Eleven|Danny gathering the team~Bellagio fountain planning~vault rehearsal beats~casino floor on the big night|slick ensemble~heist pleasure~movie-star cool~great pacing|Ocean's Eleven is remembered through the team assembly almost as much as the heist itself. The suits, the casino floors, and the easy confidence keep another watch tempting.
2001|Cult Favorite|Donnie Darko|jet engine in the house~Frank in the rabbit suit~school-day dread getting stranger~suburban nights feeling wrong|teen-cult energy~mystery hook~moody soundtrack~weird suburban pull|Donnie Darko lives on through that rabbit suit and the feeling that every suburban street has gone slightly off. The movie has been a midnight conversation starter ever since.
2001|Date Night|Moulin Rouge!|Elephant Love Medley in the club~Sparkling Diamond entrance~elephant room above the city~stage lights turning everything bigger|musical rush~romantic excess~lush visuals~high-voltage emotion|Moulin Rouge! comes back in flashes of red, gold, and Nicole Kidman making a full entrance. The songs and the speed are the reason the movie still feels like a rush.
2001|Underrated|Ghost World|record-store drifting~awkward diner conversations~Seymour's apartment and old records~Enid watching the world from a distance|offbeat humor~outsider perspective~quiet melancholy~cult-comic feel|Ghost World is mostly remembered through small conversations and the way Thora Birch watches everybody else miss the point. The record-store sadness gives the movie its shape.
2001|The One That Grows on You|A Beautiful Mind|Princeton arrival~chalkboard breakthroughs~secret-work paranoia~quiet domestic scenes after the noise dies down|performance-driven~human vulnerability~period detail~emotional payoff|A Beautiful Mind is easy to remember through the Princeton halls and the sudden turns into paranoia. The quieter family scenes are what tend to stick later.
2001|Crowd Favorite|Shrek|fairy-tale creatures dumped in the swamp~road trip with Donkey~tournament chaos~rescue at the dragon's castle|big laughs~family appeal~fresh animated style~endlessly quotable|Shrek is remembered scene by scene, from the swamp to Donkey talking without a pause to the dragon's keep. The movie had enough attitude to feel new the first time out.
2001|After Midnight|Training Day|first ride-along in the car~neighborhood visits with Alonzo in charge~bathtub-and-shotgun tension~long day turning into a trap|street-level intensity~star performance~moral pressure~unsettling momentum|Training Day is mostly one long bad ride with Denzel Washington at the wheel. The car, the neighborhoods, and the sense of being in too deep are what make it linger.

# 2002
2002|Crowd Favorite|The Lord of the Rings: The Two Towers|Helm's Deep preparations~Gollum leading the way~Rohan riders on the plain~Ents marching on Isengard|fantasy spectacle~battle scale~beloved characters~adventure momentum|Helm's Deep is the scene set people remember first, but Gollum and the Rohan plains matter just as much. The Two Towers keeps widening the world without losing its pulse.
2002|After Midnight|City of God|kids racing through the alleys~camera circling the neighborhood chaos~gang photos and fame~streets getting hotter and more dangerous|kinetic storytelling~street energy~ensemble sprawl~hard-edged momentum|City of God hits through movement and speed almost immediately. The alleys, the flash photography, and the sense that childhood is vanishing fast keep the movie alive.
2002|Big Screen Moment|Spider-Man|Peter testing his powers~upside-down kiss in the rain~Queens rooftops and web swings~Goblin attack at the festival|superhero wonder~romantic pull~city-scale action~origin-story fun|The rooftop swings and the upside-down kiss are the two big images most people keep from Spider-Man. The movie has the bright confidence of a hero story figuring itself out in public.
2002|Rewatchable|Catch Me If You Can|airport cons and uniforms~Frank reading the forged checks~cat-and-mouse phone calls~Christmas scenes with the chase still going|great pace~star chemistry~con-artist fun~period charm|Catch Me If You Can stays light on its feet because Leonardo DiCaprio and Tom Hanks keep chasing from one disguise to the next. The airport and Christmas scenes are the parts people usually name.
2002|Cult Favorite|28 Days Later|empty London walk~church discovery in the half light~supermarket run~road trip north with danger never far off|apocalyptic jolt~fast-zombie panic~bleak atmosphere~cult horror appeal|The empty London opening is still one of the strongest images the genre has. 28 Days Later keeps the roads, supermarkets, and safe houses feeling temporary.
2002|Date Night|My Big Fat Greek Wedding|family dinner chaos~Toula changing her routine~Greek relatives taking over the room~wedding day that feels like a whole neighborhood showed up|rom-com warmth~family comedy~crowd-pleasing charm~easy chemistry|My Big Fat Greek Wedding is remembered through the family swarm as much as the romance itself. Every dinner feels one step away from turning into a full event.
2002|Underrated|Adaptation.|screenwriter blocks and voice-over panic~orchid trips in Florida~twin brothers in the same room~story bending into stranger territory|meta humor~writerly anxiety~great performances~genre-bending fun|Adaptation. keeps changing shape in a way that makes the whole movie feel alive. Nicolas Cage playing against himself is the memory most people start with.
2002|The One That Grows on You|Chicago|Cell Block Tango on the stage~courtroom turning into full performance~Roxie chasing the spotlight~press and flashbulbs feeding the whole show|musical swagger~show-business satire~sharp choreography~black-and-gold style|Chicago stays in memory through stage numbers and all that brass-and-flash attitude. The courtroom material gets better once the whole performance idea settles in.
2002|Crowd Favorite|Signs|cornfield in the dark~birthday-party video everyone remembers~roof noises at night~family watching the monitor in the living room|farmhouse suspense~family focus~pop-culture scare moments~lean pacing|The cornfield and the birthday-party clip are the two moments almost everybody brings up. Signs keeps the whole story close to one family, which makes the fear feel more immediate.
2002|After Midnight|Minority Report|spider drones sweeping the apartments~mall chase with the precogs~car plant moving overhead~futures and screens filling the room|slick sci-fi design~propulsive action~concept-first thrills~future-tech imagery|Minority Report is remembered through gadgets, glass screens, and Tom Cruise running through a world that feels one step ahead of him. The spider drones and car plant are the scenes that keep coming back.

# 2003
2003|Crowd Favorite|The Lord of the Rings: The Return of the King|ride of the Rohirrim~beacon lights crossing the mountains~Shelob in the dark tunnel~crowning in the white city|sweeping payoff~battle grandeur~emotional sendoff~fantasy at full scale|The beacons, the ride at Pelennor, and the coronation are the moments most people hold onto. The Return of the King plays like a long goodbye that earns its size.
2003|After Midnight|Lost in Translation|hotel-bar quiet in Tokyo~karaoke night~city drifting through taxi windows~two people talking when the noise drops away|late-night melancholy~city mood~subtle connection~soft humor|Lost in Translation is remembered through hotel rooms, neon views, and that karaoke stretch where the whole movie seems to exhale. Tokyo gives every quiet beat a little extra glow.
2003|Big Screen Moment|Pirates of the Caribbean: The Curse of the Black Pearl|Jack Sparrow arriving on the sinking boat~blacksmith-shop sword fight~moonlit skeleton reveal~ship battle under the night sky|swashbuckling fun~star-making performance~big adventure feel~instantly quotable|The sinking-boat entrance told everybody what kind of star vehicle Pirates was about to be. The sword fight and moonlight reveal are the images people still go to first.
2003|Rewatchable|Finding Nemo|drop-off at school~jellyfish field glowing in the dark~sharks at the meeting~East Australian Current with Crush|family adventure~underwater visual fun~great character voices~comfort rewatch value|Finding Nemo has too many easy-to-remember underwater bits to fade out, especially the jellyfish and the current. The movie keeps the emotional center simple enough for every age to follow.
2003|Cult Favorite|Oldboy|hallway hammer fight~mysterious imprisonment~purple-lit search through the city~dumplings and clues piling up|stylish vengeance tale~shock-factor reputation~hard-hitting action~cult intensity|Oldboy is remembered first through that hallway fight and the locked-room setup. The movie has a bruised, feverish energy that keeps it in late-night movie talk.
2003|Date Night|Love Actually|airport arrivals and departures~cue cards at the door~Christmas pageant sweetness~London romance stories crossing paths|holiday warmth~ensemble charm~romantic comedy comfort~rewatch season appeal|Love Actually is built out of little moments people can name without trying, especially the airport and the front-door cue cards. The holiday setting keeps it returning every year.
2003|Underrated|Master and Commander: The Far Side of the World|cannon fire through the fog~shipboard surgery below deck~violin and cello in the captain's cabin~Galapagos stop before the chase begins again|seafaring immersion~practical action~period texture~great sound design|Master and Commander is remembered for the sea itself as much as the story riding on top of it. The fog attack and all that creaking ship detail do the heavy lifting.
2003|The One That Grows on You|Mystic River|street hockey in childhood~front porch and neighborhood grief~police questions closing in~Boston streets holding old damage|somber atmosphere~performance strength~working-class detail~lingering sadness|Mystic River sticks harder after some time passes because the neighborhood itself feels like part of the tragedy. Sean Penn and Tim Robbins give the whole movie a heavy pull.
2003|Crowd Favorite|Elf|Buddy in the North Pole workshop~department-store chaos~spaghetti with syrup~New York seen through Buddy's eyes|holiday laughs~instant quotables~family appeal~Will Ferrell charm|Elf is basically a stack of favorite scenes, from the syrup-covered spaghetti to Buddy wandering through New York like he has never seen a revolving door. The movie still feels like an easy holiday pickup.
2003|After Midnight|Kill Bill: Vol. 1|anime origin burst~Tokyo club showdown~snowy garden duel~Bride driving with revenge on her face|stylized action~soundtrack snap~genre mashup~iconic costume work|Kill Bill: Vol. 1 is remembered through color, music, and the snow-covered duel at the end of the trail. Every chapter has its own charge.

# 2004
2004|Crowd Favorite|Spider-Man 2|train fight over the city~Doc Ock in the hospital room~Peter trying to live without the suit~rain-soaked rescue moments|superhero peak energy~great villain~city-scale thrills~big emotional beats|The train fight and Doc Ock's metal arms in the hospital are the two images people jump to fastest. Spider-Man 2 balances New York spectacle with Peter Parker's everyday strain.
2004|After Midnight|Eternal Sunshine of the Spotless Mind|memory erasing on the beach house floor~Joel hiding Clementine inside old memories~frozen Charles River and winter walks~records and drawings tied to what is disappearing|romantic melancholy~visual inventiveness~heartbreak with humor~memory-driven structure|Eternal Sunshine comes back through fragments: winter light, collapsing rooms, and those two trying to stay inside a memory. The movie feels personal even when the images get strange.
2004|Big Screen Moment|The Incredibles|family dinner breaking apart~Dash on the water~island lair revealed~all five family members working together at speed|superhero family fun~animation craft~great action design~broad appeal|The island, Dash on the water, and the family finally syncing up are the parts most people carry away. The Incredibles has the snap of a live-action blockbuster without losing the family hook.
2004|Rewatchable|Mean Girls|cafeteria map of the cliques~Jingle Bell Rock performance~Burn Book chaos~hallways turning into a full social war|quotable comedy~teen-movie precision~great ensemble~easy replay value|Mean Girls is remembered almost entirely in bits people can quote back on command. The cafeteria layout and the Burn Book are enough to bring the whole movie into focus.
2004|Cult Favorite|Shaun of the Dead|pub plan that keeps coming back~record-throwing in the living room~walking to work while missing the crisis~siege at the Winchester|zombie-comedy balance~smart sight gags~British pub energy~cult devotion|Shaun of the Dead keeps getting bigger in memory because the jokes and zombie beats fit together so cleanly. The walk to work and the Winchester plan are the scenes nearly everybody knows.
2004|Date Night|Before Sunset|bookstore reunion~walking through Paris all afternoon~boat ride on the river~apartment conversation with the guitar nearby|conversation-driven romance~city intimacy~real-time closeness~gentle longing|Before Sunset lives on through walking and talking because the two leads make every turn feel loaded. Paris gives the whole movie a light touch.
2004|Underrated|Collateral|silver-haired driver stepping into the cab~LA glowing at night through the windows~jazz club tension~coyote crossing the empty street|night-city atmosphere~tight thriller focus~cool visual style~great two-hander|Collateral is remembered through the cab, the silver hair, and Los Angeles looking half empty and half electric. The coyote crossing is the image people mention once the rest settles in.
2004|The One That Grows on You|Sideways|wine-country drives~Miles talking about pinot noir~awkward dinner scenes~vineyards stretching out under soft light|grown-up comedy~friendship cracks~California mood~sad-funny balance|Sideways gets better later because the road trip keeps feeling more revealing the older you get. The restaurant scenes and all that wine-country air do most of the remembering.
2004|Crowd Favorite|The Notebook|summer carnival courtship~rowboat on the water~old house brought back to life~letters and time pulling in opposite directions|weepy romance~big emotional swings~period appeal~star chemistry|The rowboat and the restored house are the two images most people go to first. The Notebook stays in rotation because it goes straight for feeling and never apologizes for it.
2004|After Midnight|Million Dollar Baby|gym routines at dawn~Frankie watching from the corner~small boxing halls and hard travel~quiet hospital rooms replacing the noise|performance-led drama~sports grit~emotional weight~somber tone|Million Dollar Baby starts with the gym and stays close to the people working inside it. The shift from training rooms to hospital quiet is what many viewers remember.

# 2005
2005|Crowd Favorite|Batman Begins|escape from the temple~first glide over Gotham~Batmobile chase on the rooftops and streets~swarms filling the train line and the city below|franchise reset energy~dark-city atmosphere~great origin momentum~big action design|The glide over Gotham and the Batmobile tearing through the city are the scenes most people hold onto. Batman Begins gave the character back his shadow and a lot of force.
2005|After Midnight|Brokeback Mountain|mountain summer together~shirts in the closet~reunions that never get easier~open roads and quiet rooms between them|aching romance~landscape beauty~performance intimacy~long-lasting sadness|Brokeback Mountain is remembered through Wyoming air, that first summer, and the ache of every reunion after. Heath Ledger and Jake Gyllenhaal carry a lot with very little noise.
2005|Big Screen Moment|King Kong|Skull Island wall opening up~Kong's first appearance in the jungle~ice-skating in Central Park~Empire State Building at dusk and night|monster-movie scale~effects spectacle~old-Hollywood throwback~adventure sprawl|The island and the climb up the Empire State Building are the giant images everybody expects, and King Kong delivers both at full size. The picture runs on scale and heartbreak.
2005|Rewatchable|The 40-Year-Old Virgin|speed-dating disasters~chest-waxing scene~store hangouts with the crew~bikes and dating advice going nowhere fast|big laugh scenes~ensemble comedy~quotable bits~easy replay pull|The chest waxing and all the store talk are enough to keep The 40-Year-Old Virgin in regular rotation. Steve Carell and the supporting cast give the movie its whole comic engine.
2005|Cult Favorite|Sin City|rain and neon on the streets~yellow bastard nightmare fuel~barrooms and alleys in stark black and white~Marv bulldozing through the whole city|graphic-novel style~hard-boiled attitude~anthology energy~cult visual hook|Sin City is remembered as much for the look as anything the characters say. The rain, the coats, and the high-contrast city made the movie feel like a comic panel left open all night.
2005|Date Night|Pride & Prejudice|ballroom glare across the room~rain-soaked proposal~hand flex after the dance~sunrise walk through the field|romantic yearning~period beauty~strong chemistry~comfort rewatch appeal|Pride & Prejudice is mostly memory by gesture: a hand flex, a look across the room, a walk through the mist. The movie has a softness that keeps pulling people back.
2005|Underrated|A History of Violence|diner attack that changes everything~small-town life turning watchful~porch and stair conversations at night~old life arriving at the front door|lean tension~performance strength~small-town unease~crime-story sharpness|A History of Violence goes from ordinary-town calm to unease in almost no time. The diner scene and the front-porch aftermath are what people tend to remember.
2005|The One That Grows on You|Walk the Line|Memphis sessions~Johnny and June on the tour bus~stage banter becoming something more~prison performance with the crowd in full voice|music-biopic energy~strong chemistry~period atmosphere~great songs|Walk the Line lands first through performances and then settles in through the chemistry between Joaquin Phoenix and Reese Witherspoon. The bus rides and stage talk are the scenes that stay warm.
2005|Crowd Favorite|Harry Potter and the Goblet of Fire|Triwizard tasks beginning~Yule Ball nerves~dragon chase through the air~dark maze swallowing the champions|teen-series momentum~wizard spectacle~school-year drama~franchise scale|The tournament tasks and the Yule Ball are the two big memory markers from Goblet of Fire. The series starts feeling larger and rougher here, and people still remember the shift.
2005|After Midnight|Munich|hotel-room aftermath~operations planned in foreign apartments~Olympic footage hanging over every move~night streets in Europe turning tense|political thriller weight~moral uncertainty~procedural detail~restless momentum|Munich keeps the audience close to rooms where bad decisions are made in the dark. The missions and the unease around them are the whole point.

# 2006
2006|Crowd Favorite|The Departed|drop on the gang at the opening~elevator tension everybody knows~phone calls between both sides~Boston bars and back rooms full of pressure|crime-thriller punch~great cast~constant tension~high replay value|The elevator and the phone-game between both camps are the two memories nearly everybody shares. The Departed keeps the whole city humming with nerves.
2006|After Midnight|Pan's Labyrinth|stone maze and moonlight~chalk door on the wall~Pale Man at the table~forest and camp turning into two different worlds|dark fairy-tale mood~gorgeous design~wartime shadow~mythic imagery|The Pale Man and the chalk door are the scenes most people picture first. Pan's Labyrinth keeps fairy-tale wonder and wartime fear in the same frame.
2006|Big Screen Moment|Casino Royale|parkour chase at the construction site~airport sequence with the fuel truck~poker table stares in Montenegro~stairwell fight with the sinking silence after|franchise reboot force~physical action~cool style~new-Bond energy|Casino Royale announced a different Bond almost immediately with the parkour chase and the bruising stairwell fight. The poker table and airport sequence keep the movie locked in.
2006|Rewatchable|The Devil Wears Prada|Andy entering the office for the first time~fashion montage through the city~Runway prep in Paris~Miranda cutting the room down with one sentence|sharp comedy~fashion-world appeal~great performances~comfort rewatch value|The office, the makeover, and all those Miranda Priestly line readings are why The Devil Wears Prada stays easy to revisit. The movie knows exactly how much bite to give every scene.
2006|Cult Favorite|The Prestige|dueling magicians on the stage~transported man mystery~Tesla's machine humming in the dark~journal pages turning one obsession into another|twisty structure~stagecraft atmosphere~cult rewatch interest~obsession-driven drama|The Prestige is the kind of movie people want to circle back to once the whole trick becomes clear. The stage acts and Tesla material are the pieces that keep getting discussed.
2006|Date Night|The Holiday|two women swapping houses~cottage in the English countryside~movie-trailer flirting in LA~snowy village comfort taking over the mood|rom-com comfort~holiday glow~two-city charm~easy chemistry|The Holiday is remembered through the cottage, the California light, and the way both stories settle into comfort. The movie feels like a December blanket with better lighting.
2006|Underrated|Children of Men|coffee shop bombing at the start~car ambush in the woods~refugee camp under fire~single-shot city chaos that feels impossible|bleak future realism~technical bravura~human stakes~intense immersion|Children of Men is remembered through a handful of astonishing long takes and a future that feels too close. The woods ambush and the camp sequence are the first scenes many people reach for.
2006|The One That Grows on You|Little Miss Sunshine|yellow van refusing to start~pageant trip across the highway~family dancing to stay afloat~small motel and roadside stops|indie-road charm~family friction~sad-funny balance~gentle warmth|Little Miss Sunshine gets stronger because the family feels messier and more lovable every time the van breaks down. The road and the final pageant are what people remember most.
2006|Crowd Favorite|Borat|reporter arriving in America~rodeo sequence that sends the room sideways~hotel and dinner disasters~cross-country trip getting worse by the mile|shock-comedy energy~scene-based laughs~cultural prank appeal~instant reactions|Borat is remembered almost entirely in giant reactions, with the rodeo and dinner scenes right at the top. The whole movie feels like watching a fuse burn in public.
2006|After Midnight|The Lives of Others|surveillance headphones in the attic~Berlin apartments under watch~typewriter hidden under the floorboards~quiet acts of mercy inside a rigid system|surveillance tension~moral awakening~period detail~subtle power|The Lives of Others is remembered through listening more than action, especially up in that attic with the headphones on. The quiet changes inside the watcher are what stay with people.
"""

EXTRA_CATALOG_TEXT += """
# 2007
2007|Crowd Favorite|No Country for Old Men|coin toss at the gas station~Anton walking through the motel hall~border crossing after the wound~desert chase with the case already gone|dry menace~western-noir mood~iconic villain~lingering tension|The gas-station coin toss and those motel hallways are the first pieces most people reach for. No Country for Old Men feels stripped down and dangerous from start to finish.
2007|After Midnight|There Will Be Blood|oil derrick fire against the night~bowling alley showdown~plainview watching from the edge of the field~church scenes turning personal and ugly|towering performance~American mythmaking~slow-burn intensity~big images|There Will Be Blood is remembered through fire, oil, and Daniel Day-Lewis filling every room. The movie keeps widening without ever losing that personal hostility.
2007|Big Screen Moment|The Bourne Ultimatum|Waterloo Station chase~rooftop leap in Tangier~London newsroom pressure~Moscow and New York both feeling watched|kinetic action~franchise precision~spy-thriller urgency~great chase design|The Waterloo Station sequence is the scene set everybody remembers first, and Tangier is right behind it. The Bourne Ultimatum moves like it cannot afford to stop.
2007|Rewatchable|Superbad|liquor-store mission~party spiraling out of control~cop car ride with the wrong friends~school-year ending still a little awkward|teen-comedy gold~huge laughs~friendship core~quotable scenes|Superbad has enough famous scenes to stay on rotation all by itself, starting with the failed booze run. The movie hangs onto a real friendship under all the chaos.
2007|Cult Favorite|Zodiac|basement conversation nobody forgets~late-night ciphers and newspaper rooms~lake stabbing turning the air colder~detectives and reporters losing years to the chase|investigative obsession~serial-killer tension~period craft~cult rewatch pull|Zodiac lives on through process and dread, especially in the basement scene and all those puzzle-heavy newsroom stretches. The search itself becomes the memory.
2007|Date Night|Juno|pregnancy test in the chair~hamburger phone calls~Juno and Paulie in the track shorts~adoptive-home visits that change tone by inches|offbeat romance~sharp dialogue~indie charm~warm humor|Juno sticks through line readings and little details, from the hamburger phone to the running track. Ellen Page and Michael Cera keep the whole movie light on its feet.
2007|Underrated|Michael Clayton|opening monologue in the field~horses on the roadside~law-firm panic spreading through glass offices~late-night cab rides with nobody relaxed|adult-thriller tension~great dialogue~corporate paranoia~performance focus|Michael Clayton is remembered through boardrooms, late-night cabs, and George Clooney looking more tired every scene. The movie keeps its pressure clean and steady.
2007|The One That Grows on You|Atonement|typewriter rhythm at the opening~library tension~Dunkirk beach in one long sweep~green dress and old regret hanging over the story|period romance~formal beauty~war-time disruption~emotional aftertaste|Atonement lands first through style, then sticks because the images stay so sharp. The library, the Dunkirk beach, and that green dress do most of the remembering.
2007|Crowd Favorite|Ratatouille|Remy in the kitchen at night~Linguini trying to keep up~food critic arriving with the room tightening~Paris rooftops and restaurant light|family charm~food-movie pleasure~great animation~crowd appeal|Ratatouille remembers Paris, the kitchen rush, and Anton Ego's whole presence from the minute he sits down. The movie has warmth without losing its snap.
2007|After Midnight|Eastern Promises|steam-room fight~restaurant-book connections~midwife pulled into a darker world~London streets feeling colder by the block|crime-world tension~great performances~stark atmosphere~violent precision|The steam-room fight is the scene most people bring up first, and the rest of Eastern Promises keeps that same cold pressure. Every street and cafe feels watched.

# 2008
2008|Crowd Favorite|The Dark Knight|bank heist opening~truck flip in downtown Gotham~interrogation room with the lights on hard~hospital explosion under broad daylight|comic-book scale~great villain~citywide stakes~iconic set pieces|The bank job, the interrogation room, and that truck flip are enough to bring The Dark Knight back in seconds. Heath Ledger's Joker gave the whole movie its electricity.
2008|After Midnight|The Wrestler|Ram heading through the curtain~grocery-store grind during the week~strip-club conversations with Cassidy~old body paying the bill for every cheer|performance-driven~bruised heart~working-class grit~late-career melancholy|The Wrestler is remembered through locker rooms, deli counters, and Mickey Rourke carrying every ache in plain view. The movie feels intimate even in front of a crowd.
2008|Big Screen Moment|Iron Man|cave-built suit firing up~test flight over the desert~Tony announcing himself at the podium~home workshop turning into a full lab|franchise-launch energy~charismatic lead~metal-suit spectacle~big-screen fun|The cave escape and the first clean Iron Man flight are the two moments most people grab first. Iron Man had enough confidence to make the whole superhero era feel lighter and faster.
2008|Rewatchable|Tropic Thunder|fake trailers at the opening~jungle production falling apart~Tom Cruise dancing in the shadows of the office~everybody still acting while the bullets get real|high gag density~ensemble comedy~scene-stealing turns~easy replay value|Tropic Thunder survives on bit after bit, starting with the fake trailers and never really slowing down. The cast keeps finding new ways to go too far.
2008|Cult Favorite|Let the Right One In|playground bullying at dusk~pool sequence under the surface~snowy apartment blocks~two lonely kids meeting around the edges of the night|winter horror mood~quiet emotion~vampire story refreshed~haunting atmosphere|Let the Right One In keeps getting brought up through snow, silence, and that pool scene nobody forgets. The movie is cold in the best possible way.
2008|Date Night|Mamma Mia!|island arrival in the sunlight~Dancing Queen in the village~three possible dads landing at once~wedding day turning into a whole singalong|feel-good energy~vacation glow~big songs~group-movie charm|Mamma Mia! is remembered through sun, songs, and everybody committing fully to the island mood. The whole thing feels like a vacation that happened to become a musical.
2008|Underrated|Frost/Nixon|backstage nerves before the taping~television lights on the interview set~late-night strategy talks~Nixon's phone call changing the air|talk-heavy tension~great performances~historical drama~surprising suspense|Frost/Nixon turns televised conversation into a real event, especially once the taping begins. The lights, the prep, and the pressure on both men are what people remember.
2008|The One That Grows on You|Slumdog Millionaire|game show questions locking with the past~Mumbai train-hopping and chases~dance and color under city lights~studio silence before the next answer|storytelling momentum~romantic thread~big-energy editing~crowd-pleasing uplift|Slumdog Millionaire is remembered through motion, music, and that game-show frame holding everything together. The movie moves so fast that the feelings arrive almost by surprise.
2008|Crowd Favorite|WALL-E|lonely cleanup routine on Earth~hello from Eve changing the whole mood~dance in space outside the ship~plant in the boot held like a small miracle|wordless charm~visual storytelling~family appeal~big heart|The opening stretch on Earth and the dance in space are the two memory anchors for WALL-E. The movie gets a lot done with very little noise.
2008|After Midnight|Doubt|sermons hitting the room hard~school hallway confrontations~office scenes with no easy answer~winter light around the church and school|actor showcase~moral uncertainty~talk-driven tension~somber mood|Doubt is remembered through voices in small rooms and the feeling that certainty keeps slipping away. Meryl Streep and Philip Seymour Hoffman give every exchange real weight.

# 2009
2009|Crowd Favorite|Avatar|first flight on a banshee~Pandora glowing at night~Jake entering the avatar body~floating mountains opening up across the screen|immersive spectacle~world-building scale~big-screen wonder~event-movie feel|Pandora at night and the first banshee flight are the scenes most people bring up without thinking. Avatar was built to be seen huge, and that part still shows.
2009|After Midnight|The Hurt Locker|bomb suit walking into the street~desert sniper standoff~night raid under green light~James back home staring at a cereal aisle|war-zone tension~jittery immediacy~adrenaline addiction~nervy pacing|The Hurt Locker is remembered through pure tension, especially whenever the suit goes on and the street clears out. The grocery-store scene is the one people mention after the noise fades.
2009|Big Screen Moment|Star Trek|Kirk stealing the car at the start~jump to warp and first look at the bridge~red matter chaos~crew finally assembled and moving in sync|franchise revival~big effects fun~cast chemistry~crowd-friendly pace|The bridge reveal and the shift to warp are the moments most people still picture first. Star Trek brought a lot of old iconography back with much more speed.
2009|Rewatchable|The Hangover|hotel room after the blackout~tiger in the bathroom~missing groom panic~walking the Strip with no idea what happened|high-concept comedy~scene-based laughs~party-movie energy~easy replay pull|The wrecked hotel room is enough to bring The Hangover right back. Every clue after that feels like the setup for one more big laugh.
2009|Cult Favorite|Moon|Sam talking to himself and not quite~lunar rover and silent gray landscape~computer voice filling the room~small station life getting stranger by the day|lonely sci-fi mood~minimalist tension~great performance~cult-favorite intimacy|Moon stays with people because the station feels so small and the loneliness feels so complete. Sam Rockwell and that gray lunar setting do all the work they need.
2009|Date Night|(500) Days of Summer|Ikea wandering together~split-screen expectations and reality~karaoke and rooftop glow~city walks after the weather shifts|rom-com remix~playlist appeal~stylized feelings~youthful heartache|(500) Days of Summer is remembered through little Los Angeles moments and a soundtrack that keeps the whole thing moving. The split-screen scene is usually the first one people mention.
2009|Underrated|Crazy Heart|bad motel rooms on the road~small-bar performances~visit with Jean and Buddy~quiet mornings with the guitar close by|weathered performance~country-music atmosphere~roadweariness~earned emotion|Crazy Heart hangs on Jeff Bridges and the roads he keeps taking even when they all look the same. The bars, the motels, and the songs are what stay behind.
2009|The One That Grows on You|Up|opening life montage~house lifting into the sky~balloon-filled silhouette above the clouds~Carl and Russell learning each other by degrees|big emotion early~family-adventure warmth~beautiful images~unexpected melancholy|Up is remembered first through the opening montage and the house in the sky, but the friendship in the middle is what really lasts. The movie gets gentler as memory settles in.
2009|Crowd Favorite|Inglourious Basterds|farmhouse opening under a too-calm sky~bear Jew entrance everybody waits for~tavern scene turning bad one detail at a time~movie theater becoming the whole battlefield|talk-heavy tension~alternate-history shock~scene-stealing villain~big crowd reactions|The farmhouse opening and the tavern sequence are enough to keep Inglourious Basterds alive in anybody's head. Christoph Waltz changed the whole energy of the room whenever he arrived.
2009|After Midnight|A Serious Man|opening fable in the snow~roof checks and bad omens~rabbi visits going nowhere helpful~suburban life getting stranger and less explainable|deadpan unease~suburban absurdity~moral haze~Coen-brothers sting|A Serious Man is remembered through ordinary spaces that keep turning less ordinary by the minute. The movie never raises its voice, which is part of the joke.

# 2010
2010|Crowd Favorite|Inception|city folding over itself~hallway fight with gravity gone~spinning hallway hotel stretch~kick sequence hitting across multiple layers|big-concept spectacle~dream-world visuals~action precision~event-movie rush|The folding city and the hallway fight are the images almost everybody goes to first. Inception turned a puzzle box into something huge and physical.
2010|After Midnight|Black Swan|mirror practice and cracking nerves~backstage pressure~night out turning feverish~white feathers and stage light taking over|psychological intensity~body-horror edge~dance-world pressure~performance showcase|Black Swan is remembered through mirrors, rehearsal rooms, and Natalie Portman looking less certain every minute. The movie keeps beauty and panic pressed together.
2010|Big Screen Moment|Toy Story 3|daycare reveal with the new toys~Ken and Barbie comic detour~escape planning in the playroom~big action in the trash yard|family emotion~animated set pieces~franchise payoff~beloved characters|Toy Story 3 has the daycare, the escape, and one of Pixar's biggest emotional reactions all sitting in plain view. The movie knows how much history the audience is carrying in.
2010|Rewatchable|The Social Network|opening breakup talk~crew race through Harvard nightlife~depositions cutting across the rise of the site~Sean Parker entering and changing the tempo|fast dialogue~startup mythology~sharp editing~repeat-watch appeal|The opening conversation and all those deposition-room cuts are enough to make The Social Network instantly recognizable. Aaron Sorkin's dialogue gives the whole movie its velocity.
2010|Cult Favorite|Scott Pilgrim vs. the World|video-game battle graphics in real life~band practice in the apartment~League of Evil Exes fights~Toronto streets lit like an arcade|comic-book energy~hyper-stylized editing~cult humor~music-scene appeal|Scott Pilgrim is remembered through graphics, music, and pure editing speed. The movie feels like somebody finally let a favorite comic jump straight into motion.
2010|Date Night|Blue Valentine|ukulele and doorway flirtation~small motel getaway~dancing and drinking in the city~domestic spaces losing their warmth|raw romance~intimate performances~sad honesty~close-up emotion|Blue Valentine is remembered through little moments of closeness before the air starts to go out of the room. Michelle Williams and Ryan Gosling keep the whole movie painfully near.
2010|Underrated|Winter's Bone|Ozark woods in cold light~Ree knocking on doors that do not welcome her~barn and back-road threats~family loyalty turning hard and silent|rural noir mood~breakout performance~hard realism~quiet danger|Winter's Bone lives on through its landscape as much as its story. Jennifer Lawrence moving through those roads and porches is the whole memory.
2010|The One That Grows on You|True Grit|snake pit shock~horseback ride through open country~sharpshooter tradeoffs across the valley~Mattie and Rooster needling each other all the way through|western humor~stern adventure~great performances~old-fashioned craft|True Grit gets better with time because the banter and the dust settle in together. Jeff Bridges and Hailee Steinfeld give the movie its backbone.
2010|Crowd Favorite|How to Train Your Dragon|Toothless first emerging from the dark~flying over the water together~training ring turning upside down~village battle with dragons filling the sky|family adventure~soaring visuals~big emotional hook~franchise-start charm|The first real flight with Toothless is the scene most people still carry around. How to Train Your Dragon found a gentle center inside all that airborne spectacle.
2010|After Midnight|Shutter Island|ferry arriving through the fog~storm shutting the island down~cave in the rocks~institution halls and questions that never ease up|gothic atmosphere~mystery pressure~moody visuals~island-thriller pull|Shutter Island is remembered through fog, storm light, and Leonardo DiCaprio walking deeper into a place that never feels stable. The island itself does half the acting.

# 2011
2011|Crowd Favorite|Harry Potter and the Deathly Hallows: Part 2|escape from Gringotts on the dragon~Hogwarts turning into a battlefield~stone courtyard filling with fighters~room of requirement flames chasing everybody through|franchise payoff~wizard spectacle~emotional sendoff~massive event feel|The dragon, the castle, and the final return to Hogwarts are the images most people kept from the last stretch. Deathly Hallows: Part 2 had the feeling of a generation arriving for one last night.
2011|After Midnight|Drive|elevator scene that changes everything~night rides through Los Angeles~opening getaway with the police overhead~pink title cards over the city|neon-noir mood~minimalist cool~sudden violence~cult-driver energy|Drive is remembered through the music, the nighttime roads, and that elevator sequence. The movie keeps its cool right up until it absolutely does not.
2011|Big Screen Moment|Mission: Impossible – Ghost Protocol|Burj Khalifa climb~Kremlin set piece~parking-garage chase in the sandstorm~team finally syncing up on the impossible job|stunt spectacle~team-based thrills~franchise lift~big-screen action|The Burj Khalifa climb is the scene everybody starts with, and for good reason. Ghost Protocol gave the series a new burst of speed.
2011|Rewatchable|Bridesmaids|dress-shop disaster~plane ride from hell~engagement-party awkwardness~food poisoning turning the whole outing upside down|big laughs~friendship core~scene-stealing ensemble~easy replay value|Bridesmaids survives on giant comedy set pieces, but the friendship friction under them gives the movie extra life. The plane and the dress shop are the scenes nearly everyone remembers.
2011|Cult Favorite|Attack the Block|council-estate staircase chases~glowing-teeth creatures in the dark~fireworks over the block~crew regrouping with improvised weapons|creature-feature fun~urban energy~comic edge~cult devotion|Attack the Block keeps its whole world on one estate and turns that limitation into energy. The creatures with those glowing mouths are the image people carry first.
2011|Date Night|Midnight in Paris|night car arriving out of nowhere~Paris walks turning magical~writers around the table talking like legends in the room~museum and market daylight after the spell lifts|romantic fantasy~city glow~literary charm~easy comfort|Midnight in Paris is remembered through moonlight, old Paris, and the simple pleasure of walking into another era for a while. The city does a lot of the seducing.
2011|Underrated|Moneyball|empty Oakland stadium seats~trade calls at the desk~Brad Pitt and Jonah Hill in the office building the roster~batting-cage frustration meeting cold math|sports-process appeal~great dialogue~smart structure~quiet emotional core|Moneyball is remembered through meetings and numbers in a way that still feels cinematic. The draft-board and trade-call scenes are the hooks.
2011|The One That Grows on You|The Artist|silent-screen stardom on full display~sound-era panic closing in~dance numbers with old-Hollywood bounce~dog and leading man carrying a room together|old-Hollywood charm~formal playfulness~sweet emotion~performance glow|The Artist gets more charming in memory because the style never feels like a stunt. Jean Dujardin, Berenice Bejo, and that dog give the movie most of its heartbeat.
2011|Crowd Favorite|The Help|kitchen-table stories finally being written down~pie delivered with a smile~bridge-club barbs~women finding room to say what has been unsaid|ensemble strength~crowd-pleasing drama~humor and hurt~memorable performances|The Help is remembered through kitchens, living rooms, and moments when somebody finally says what everybody else keeps swallowing. The cast does a lot of the lifting.
2011|After Midnight|Tinker Tailor Soldier Spy|circus gone bad in Budapest~safe house conversations in low light~Christmas party glances that mean more later~quiet office work turning into a hunt|cold-war atmosphere~spycraft patience~dense intrigue~moody restraint|Tinker Tailor Soldier Spy stays in memory through glances, files, and rooms where almost nobody speaks above a murmur. The Christmas party is the scene many people circle back to.

# 2012
2012|Crowd Favorite|The Avengers|team finally circling up in New York~helicarrier under attack~Loki testing everybody in one room~battle overhead with the city wide open below|superhero team-up thrill~crowd reaction energy~big action design~event-movie appeal|That spinning shot of the team in New York is still the image most people carry first. The Avengers felt like a payoff years in the making.
2012|After Midnight|Zero Dark Thirty|late-night briefings and map rooms~raid preparation down to the smallest detail~compound tension in the dark~years of searching wearing everybody down|procedural intensity~national-mission focus~quiet tension~somber realism|Zero Dark Thirty is remembered through offices, screens, and that long night raid holding its breath. The years of waiting are part of what gives the movie its weight.
2012|Big Screen Moment|Skyfall|train crash over the street~Shanghai tower fight in silhouette~casino at Macau glowing over the water~home turf showdown on the moors|stylish Bond scale~great visuals~action spectacle~franchise reinvention|Skyfall keeps handing over big images, from Shanghai glass to the burning house on the moors. The movie had more visual confidence than almost anything around it.
2012|Rewatchable|21 Jump Street|undercover-school panic~party with everything going wrong~chemistry between Schmidt and Jenko settling in~car chase with very bad decisions stacked on top|buddy-comedy fun~surprising charm~big laughs~easy replay value|21 Jump Street works because Jonah Hill and Channing Tatum find the right dumb-smart rhythm almost immediately. The party and car-chase stretches keep the whole thing moving.
2012|Cult Favorite|The Cabin in the Woods|cabin door finally opening~control-room workers treating horror like office routine~elevator of nightmares~whiteboard betting turning into a very bad idea|meta-horror fun~genre-savvy energy~wild payoff~cult rewatch appeal|The Cabin in the Woods is remembered through the control room as much as the cabin itself. Once those elevators open, the movie goes from clever to full-on gleeful chaos.
2012|Date Night|Silver Linings Playbook|awkward family dinner energy~dance rehearsal getting closer than expected~football Sundays filling the house with noise~late-night walk and trash-bag honesty|romantic spark~messy warmth~great chemistry~talky emotional pull|Silver Linings Playbook is remembered through rehearsals, family noise, and two people trying to stay upright at the same time. Jennifer Lawrence and Bradley Cooper give the movie its spark.
2012|Underrated|Beasts of the Southern Wild|Hushpuppy running through the bayou~father and daughter in the trailer home~storm and flood changing the whole landscape~mythic beasts in the distance|poetic imagery~child's-eye perspective~regional atmosphere~emotional force|Beasts of the Southern Wild stays in memory through water, fire, and Quvenzhane Wallis seeing the world at a tilt. The movie feels rough-hewn in a good way.
2012|The One That Grows on You|Moonrise Kingdom|young lovers running into the woods~island scout camp routines~storm rolling toward the church and the shoreline~handwritten letters and small acts of planning|storybook style~youthful sincerity~visual design~gentle comedy|Moonrise Kingdom settles in through color, letters, and all that island weather. The movie gets sweeter once the perfect framing stops being the main thing you notice.
2012|Crowd Favorite|Django Unchained|dentist wagon arriving in the snow~plantation house under candlelight~shootout in the mansion~blue suit swagger and revenge in plain view|revisionist-western energy~star charisma~big crowd reactions~scene-based appeal|Django Unchained is remembered through entrances, line readings, and that mansion shootout. The movie runs loud and confident the whole way.
2012|After Midnight|Argo|hostage escape plans in offices and on storyboards~fake-sci-fi production coming together~airport sequence with the nerves fully exposed~1970s Hollywood and diplomacy colliding|fact-based suspense~industry-insider hook~tense finale~period texture|Argo turns meetings, cover stories, and airport waiting into something genuinely tense. The fake-movie angle is the part people still bring up first.
"""

EXTRA_CATALOG_TEXT += """
# 2013
2013|Crowd Favorite|Frozen|Let It Go on the mountain~Anna and Olaf crossing the snow~ice palace reveal~sister reunion carrying the whole story|family phenomenon~big songs~Disney iconography~crowd-pleasing emotion|The ice palace and Let It Go are the images almost everybody starts with. Frozen also stayed around because the sister story gave all that spectacle a real center.
2013|After Midnight|12 Years a Slave|violin and ballroom life before the rupture~hanging scene stretched into unbearable time~cotton fields under punishing light~Solomon trying to keep hold of himself in impossible rooms|historical weight~harrowing realism~great performances~lasting emotional force|12 Years a Slave is remembered through a handful of scenes that never really leave once they land. The fields, the silence, and Chiwetel Ejiofor's face carry the whole film.
2013|Big Screen Moment|Gravity|opening drift in orbit~debris storm hitting out of nowhere~fire inside the capsule~Earth hanging below almost every frame|space suspense~big-screen immersion~technical bravura~two-hander intensity|Gravity is remembered through movement and silence, especially in that opening drift and the first debris hit. The movie was built to make the room feel weightless and dangerous at the same time.
2013|Rewatchable|The Wolf of Wall Street|first giant office speech~penny-stock boiler room~yacht excess spinning out~country-club and country-road chaos|wild energy~scene-based comedy~star turn~great replay value|The Wolf of Wall Street is almost all big scenes, and a lot of them hit hard enough to stay in pop memory. Leonardo DiCaprio sets the pace and almost nobody else gets to breathe.
2013|Cult Favorite|The Conjuring|hide-and-clap in the dark~basement door and the cold stairs~possession building inside the farmhouse~investigators arriving with a different kind of calm|old-school haunted-house chills~strong scare construction~period horror mood~cult-favorite polish|The Conjuring keeps getting remembered through the clap game and that basement staircase. The farmhouse and all the practical scare work gave the movie real staying power.
2013|Date Night|Before Midnight|hotel getaway at the coast~long walk through Greece~dinner table with talk about time and marriage~room conversation when the charm gives way|adult romance~talk-driven intimacy~sunlit setting~bittersweet honesty|Before Midnight is remembered through talking, walking, and one hotel room where everything sharpens at once. The movie keeps the romance alive by letting the rough parts speak too.
2013|Underrated|Inside Llewyn Davis|club performances in near-darkness~orange cat wandering in and out of the day~winter streets in Greenwich Village~road trip to Chicago with no comfort anywhere|folk-scene texture~dry humor~sad drift~beautiful music|Inside Llewyn Davis sticks through the songs and all that cold city movement. Oscar Isaac and the cat do a lot of the heavy lifting.
2013|The One That Grows on You|Her|letter-writing office in warm light~operating system voice becoming a real presence~city rooftops at dusk~subway and beach scenes feeling oddly intimate|future-romance softness~lonely-city mood~gentle sci-fi~emotional afterglow|Her gets richer later because the movie keeps everything so close to daily life. The voice in the ear and the warm city light are what people remember most.
2013|Crowd Favorite|The Hunger Games: Catching Fire|victory tour under heavy pressure~clock-arena reveal~fog and monkey attacks closing in~elevator ride and team formation before the Games|YA-franchise momentum~arena spectacle~fan-favorite stakes~strong heroine|Catching Fire is remembered through the clock arena and the feeling that the scale suddenly jumped. Jennifer Lawrence keeps the whole thing grounded even when the world gets bigger.
2013|After Midnight|Prisoners|stormy neighborhoods and headlights in the dark~van chase and abduction panic~rain-soaked searches~interrogation and basement dread hanging over everything|grim tension~great performances~suburban unease~hard moral pressure|Prisoners is remembered through rain, flashlights, and that heavy suburban dread that never really lifts. Hugh Jackman and Jake Gyllenhaal give the movie its whole pressure system.

# 2014
2014|Crowd Favorite|Guardians of the Galaxy|Star-Lord dancing through the ruins~prison-break team-up~Awesome Mix playing over the whole ride~final dance-off that nobody saw coming|comic-book fun~soundtrack appeal~ensemble chemistry~space-adventure bounce|The prison break, the soundtrack, and that final dance-off are the scenes almost everybody mentions first. Guardians of the Galaxy had enough looseness to feel different right away.
2014|After Midnight|Whiplash|first rehearsal under Fletcher's stare~bleeding hands at the drum kit~car crash before the stage~final performance turning into a war of wills|musical intensity~performance fireworks~adrenaline rush~obsession on display|Whiplash is remembered through the drum kit, the shouting, and that final stage stretch. Miles Teller and J.K. Simmons make every rehearsal feel like hand-to-hand combat.
2014|Big Screen Moment|Interstellar|cornfield chase and drone overhead~launch from Earth~dock sequence with the clock ticking~waves towering over the tiny craft|cosmic scale~big-screen awe~father-daughter emotion~Hans Zimmer thunder|Interstellar gives people a lot to remember, from the launch to the wave planet to the spinning dock. The movie goes huge but keeps coming back to one family line.
2014|Rewatchable|The Grand Budapest Hotel|hotel lobby in perfect symmetry~funicular and mountain retreat~prison escape with the pastries~ski-chase and monastery turns|stylized comedy~visual comfort~ensemble charm~repeat-watch density|The Grand Budapest Hotel is almost all instantly recognizable images, starting with the lobby and never really stopping. Every revisit finds another joke or detail tucked into the frame.
2014|Cult Favorite|John Wick|nightclub assault with the lights strobing~house invasion with the car waiting outside~dog and car pushing him back into the world~Continental rules changing the whole shape of the story|action purity~underworld mythmaking~clean stunt design~cult-franchise spark|John Wick is remembered through the nightclub, the house, and the feeling that one hitman could shift an entire underworld. The movie made stripped-down action feel sharp again.
2014|Date Night|The Fault in Our Stars|support-group meet-cute~Amsterdam trip and canal scenes~Anne Frank House visit~small rituals around illness and young love|tearjerker romance~young-lead chemistry~travel-movie glow~emotional directness|The Fault in Our Stars is remembered through Amsterdam and a lot of scenes where two people are trying to be normal in bad circumstances. The movie goes straight for feeling and people remember that.
2014|Underrated|Edge of Tomorrow|beach landing turning into instant disaster~day resetting in the barracks~training with Rita getting sharper each time~helicopter and urban-war chaos near the end|time-loop action~great pacing~smart concept~sci-fi combat fun|Edge of Tomorrow is remembered through repetition done right, especially the beach landing and all that training with Emily Blunt. The movie keeps improving every time the day resets.
2014|The One That Grows on You|Boyhood|summer afternoons changing over years~family moves and new kitchens~graduation arriving almost before you notice~small routines carrying more weight with time|life-in-passing feel~natural performances~quiet accumulation~memory-like structure|Boyhood gets stronger later because the whole point is the accumulation. The kitchens, cars, and everyday conversations are the real set pieces.
2014|Crowd Favorite|Gone Girl|media circus after the disappearance~Amy's diary voice taking over~suburban house turned into a stage~every interview making the marriage look different|twisty thriller~media satire~sharp performances~big hook energy|Gone Girl is remembered through the missing-person setup and the way every new detail changes the story people think they are watching. Rosamund Pike gives the movie a very sharp edge.
2014|After Midnight|Nightcrawler|nighttime crash-scene hustle~Louis Bloom learning the rules faster than anybody wants~television station bargaining for worse footage~Los Angeles glowing cold under all that breaking news|urban noir mood~media-world bite~creepy central performance~late-night atmosphere|Nightcrawler keeps coming back through the van, the police tape, and Jake Gyllenhaal's eyes under city neon. The whole movie feels like Los Angeles at 3 a.m.

# 2015
2015|Crowd Favorite|Mad Max: Fury Road|sandstorm swallowing the chase~guitar rig on the war convoy~Furiosa steering into open desert~return run back through the canyon and the crowd|relentless action~practical spectacle~striking design~pure momentum|Mad Max: Fury Road is remembered through movement and color almost immediately, especially the storm and the convoy. The movie barely pauses long enough for anyone to catch a breath.
2015|After Midnight|Spotlight|reporters in the archive room~door-knocking around Boston parishes~phone calls and legal files lining up~small newsroom decisions carrying a lot of weight|journalism process~quiet outrage~ensemble precision~fact-driven tension|Spotlight is remembered through ordinary reporting work made urgent by what it uncovers. The archives, the phone calls, and the newsroom meetings are the memory set.
2015|Big Screen Moment|The Martian|botanical setup on Mars~launch and docking plans~storm on the red surface~Matt Damon making science look like survival|space-adventure scale~problem-solving pleasure~big crowd appeal~humor under pressure|The Martian is remembered through potatoes, dust storms, and all the cheerful problem-solving under impossible conditions. The movie keeps the science fun without losing the danger.
2015|Rewatchable|Creed|first gym sessions under Rocky's eye~single-shot fight energy~bike riders running alongside Adonis~father's shadow hanging over the ring walk|sports-drama lift~legacy-story emotion~great training scenes~crowd-pleasing finish|Creed brought the old franchise back by finding fresh blood and a lot of heart. The training runs and that first big fight are the parts most people carry away.
2015|Cult Favorite|Ex Machina|glass house in the woods~dance scene that breaks the tension sideways~test sessions with Ava~hallways and key cards changing what feels safe|techno-thriller chill~minimalist tension~great design~cult discussion magnet|Ex Machina is remembered through the house, the dance scene, and all the quiet test conversations. The movie keeps everything sleek and a little poisonous.
2015|Date Night|Carol|department-store glance across the room~train sets and holiday windows~road trip in winter light~gloves and cigarettes carrying half the feeling|romantic longing~period elegance~performance intimacy~quiet heat|Carol is remembered through looks, gloves, and the kind of silence that says more than a speech would. Cate Blanchett and Rooney Mara keep the whole movie humming at a low frequency.
2015|Underrated|Straight Outta Compton|studio sessions shaping the sound~Detroit concert tension~group breakups under business pressure~crowds answering the music at full volume|music-biopic charge~group chemistry~industry conflict~crowd energy|Straight Outta Compton is remembered through studio sessions and live shows that feel like whole rooms getting jolted awake. The movie carries a lot of momentum on pure sound and attitude.
2015|The One That Grows on You|Room|small routines inside the room~Jack seeing the world beyond it for the first time~mother and son rebuilding ordinary life~objects from the old space carrying new meaning|intimate drama~strong performances~mother-child bond~emotional aftereffect|Room gets heavier after the first watch because the little routines and objects stay with you. Brie Larson and Jacob Tremblay give the movie a very close emotional focus.
2015|Crowd Favorite|Inside Out|core memories glowing on the shelves~headquarters chaos~train of thought and dream studio detours~Sadness and Joy finally understanding each other|family animation~inventive world-building~emotional clarity~memorable characters|Inside Out is remembered through color, clever visual ideas, and a handful of emotions that became characters overnight. The movie gave people a language they kept using after the credits.
2015|After Midnight|Sicario|border crossing at dusk~traffic-jam ambush~night-vision tunnel approach~Emily Blunt caught between agencies and methods|borderland tension~grim atmosphere~thriller precision~stark visuals|Sicario is remembered through the border convoy and the tunnel sequence more than anything else. The movie keeps the audience right beside somebody who can never fully see the board.

# 2016
2016|Crowd Favorite|La La Land|traffic-jam opening on the freeway~planetarium dance among the stars~sunset tap number in the hills~audition carrying the whole dream in one room|musical romance~color and movement~old-Hollywood affection~big emotional pull|La La Land is remembered through the freeway, the planetarium, and those twilight dance scenes all over Los Angeles. The movie wears its love of movie musicals out in the open.
2016|After Midnight|Moonlight|night swim in blue light~school and neighborhood pressure~diner reunion years later~Miami streets and apartments shaping every chapter|lyrical intimacy~three-part structure~beautiful color~deep emotional resonance|Moonlight stays with people through touch, color, and the way each chapter reshapes the same life. The night swim and the diner are the scenes most often mentioned.
2016|Big Screen Moment|Rogue One: A Star Wars Story|first trip to Jedha~beach battle on Scarif~AT-ACT walkers in the surf~team pushing through the mission one beat at a time|war-movie scale~franchise iconography~team sacrifice energy~big-screen action|The beach battle and the final push through Scarif are the parts most people pull up first. Rogue One found a gritty corner of Star Wars and filled it with scale.
2016|Rewatchable|Deadpool|highway fight with the count already running~opening credits joke~tiny apartment and blind-roommate banter~final showdown keeping the same rude energy|superhero-comedy snap~constant jokes~antihero appeal~easy replay value|Deadpool is remembered through line readings and action bits that refuse to get solemn. The highway opening told the audience exactly what kind of ride it was.
2016|Cult Favorite|The Witch|black goat in the yard~forest at the edge of the farm~night prayers going nowhere comforting~family table scenes turning harder every day|period horror mood~folk dread~slow-burn menace~cult horror pull|The Witch is remembered through woods, candlelight, and a family house that never feels safe for a second. The movie keeps the fear old and quiet.
2016|Date Night|Sing Street|school-band tryouts~music videos made out of almost nothing~harbor walks and young plans~songs growing with the relationship|music-driven romance~coming-of-age charm~80s feel~earnest heart|Sing Street is remembered through songs and little bursts of homemade style. The band scenes and the harbor give the whole movie a lift.
2016|Underrated|Hell or High Water|bank robberies under a hot sky~brothers on empty Texas roads~ranger talk over lunch~quiet casino detour before the pressure closes in|modern-western feel~tight dialogue~working-class anger~landscape mood|Hell or High Water keeps its whole identity in the roads, diners, and dry plains around the story. Jeff Bridges and Ben Foster give the movie most of its grit.
2016|The One That Grows on You|Manchester by the Sea|cold harbor mornings~Lee handling ordinary tasks without ease~flashbacks that hit when the room goes quiet~family talks that never quite straighten out|grief in plain clothes~strong performances~New England mood~lingering sadness|Manchester by the Sea gets heavier later because almost every scene feels ordinary on the surface. Casey Affleck and the winter harbor do the slow work.
2016|Crowd Favorite|Zootopia|city train arrival~DMV sloth scene~Nick and Judy turning into a real team~rainforest district and city sprawl showing how big the world is|family comedy~world-building fun~buddy-cop charm~smart crowd appeal|Zootopia is remembered through the sloths, the train, and the sheer size of the city opening up around the leads. The movie had a lot more snap than people expected from the setup.
2016|After Midnight|Arrival|shell-like ships over open land~first steps into the chamber~whiteboard language work~memories and time changing shape around the story|thoughtful sci-fi~lingering emotion~great sound and design~quiet awe|Arrival is remembered through the ships, the chamber, and the patient work of trying to understand something unknown. The movie keeps its emotions folded into the concept.

# 2017
2017|Crowd Favorite|Get Out|weekend arrival at the house~garden party under a smile that feels wrong~sunken place visual everybody remembers~auction and basement truths hiding under politeness|social-horror bite~crowd reaction power~memorable imagery~sharp satire|Get Out is remembered through the house, the party, and the sunken place almost immediately. Jordan Peele gave horror one of its most quoted images in years.
2017|After Midnight|Phantom Thread|dress fittings as ritual~mushroom omelet tension~breakfast-table power struggles~country house calm turning strangely hostile|high-style intimacy~performance showcase~romance with a knife edge~period elegance|Phantom Thread lives on through breakfast scenes and dress fittings that somehow feel like duels. Daniel Day-Lewis and Vicky Krieps make every quiet room feel loaded.
2017|Big Screen Moment|Dunkirk|beach lines waiting under the sky~dogfights above the water~small boats heading in from home~mole and breakwater under constant threat|war-spectacle immersion~sound-driven suspense~big-screen urgency~three-track structure|Dunkirk is remembered through scale and sound more than speech, especially on the beach and in the air. The movie works like a pressure machine.
2017|Rewatchable|Baby Driver|opening getaway synced to the song~coffee run still moving to the beat~warehouse arms deal cracking apart~car chases that feel choreographed by the playlist|music-action blend~stylish pacing~repeat-watch appeal~cool factor|Baby Driver is remembered through the opening escape and the way the music seems to run the wheel. The soundtrack and stunt timing make it easy to replay.
2017|Cult Favorite|Blade Runner 2049|sea wall and gray skyline~Vegas orange dust~hologram giant over the street~snow falling around the final confrontation|future-noir beauty~slow-burn sci-fi~huge visuals~cult reverence|Blade Runner 2049 stays alive through scale, color, and all those haunted city spaces. The sea wall, Vegas, and the hologram skyline are the memory anchors.
2017|Date Night|Call Me by Your Name|bike rides through the Italian summer~dancing in the small-town square~lazy meals and afternoon light~monuments and long walks turning into something else|summer romance~lush atmosphere~intimate emotion~sunlit melancholy|Call Me by Your Name is remembered through light, music, and a summer that feels too short while it is happening. The bike rides and square scenes do most of the work.
2017|Underrated|The Florida Project|motel kids roaming through tourist country~purple walls and bright heat~ice-cream runs and trouble around every corner~Willem Dafoe trying to keep the place standing|child's-eye perspective~motel-strip atmosphere~sad-funny edges~great supporting turn|The Florida Project sticks through color and the odd mix of childhood play with adult instability sitting right beside it. The motel setting is unforgettable.
2017|The One That Grows on You|Lady Bird|Catholic-school routines~college dreams pointed toward the East Coast~mother-daughter fights in the car~Sacramento streets that look different once she leaves|coming-of-age honesty~sharp humor~mother-daughter tension~specific place feeling|Lady Bird gets better with time because Sacramento and that mother-daughter bond feel so specific. The car fights and school scenes are the parts people carry first.
2017|Crowd Favorite|Coco|Land of the Dead reveal~Remember Me carrying different meanings~bridge of petals across the world~music in the family square and the shoe shop|family emotion~music-driven story~visual spectacle~crowd-pleasing heart|Coco is remembered through color, songs, and one of Pixar's biggest visual reveals. The movie keeps the family thread strong enough to hold all that brightness.
2017|After Midnight|Three Billboards Outside Ebbing, Missouri|billboards going up outside town~police-station tension~small-town bars and living rooms filling with anger~unlikely alliances forming in rough ways|small-town heat~actor fireworks~dark humor~anger that lingers|Three Billboards is remembered through the signs themselves and the way they poison every room after they go up. Frances McDormand gives the movie its whole front edge.

# 2018
2018|Crowd Favorite|Black Panther|Wakanda reveal from the air~waterfall challenge~casino fight in Busan~tribes gathering under the mountain throne|superhero spectacle~cultural impact~world-building scale~crowd energy|The Wakanda reveal and the waterfall challenge are the first images most people bring up. Black Panther felt like a full world arriving all at once.
2018|After Midnight|Roma|street and courtyard routines in black and white~beach rescue under the waves~student unrest sweeping the city~quiet domestic work carrying a whole life|beautiful realism~memory-piece structure~visual elegance~deep feeling|Roma is remembered through floor tiles, street noise, and one beach sequence that hit a lot of people very hard. The movie makes ordinary space feel monumental.
2018|Big Screen Moment|Spider-Man: Into the Spider-Verse|leap of faith off the tower~comic-book panels turning into full motion~subway battle with multiple Spider-people~collider opening the sky over Brooklyn|animation breakthrough~comic-book style~young-hero energy~big-screen color|The leap of faith shot is the image people reach for first, and nothing else looked quite like it that year. Into the Spider-Verse felt brand new from frame one.
2018|Rewatchable|Mission: Impossible – Fallout|HALO jump into the storm~bathroom fight that keeps escalating~helicopter chase in the mountains~Paris motorcycle run with no room to spare|stunt spectacle~franchise precision~breathless pace~easy replay value|Fallout is remembered through stunts almost immediately, especially the bathroom fight and that helicopter chase. The whole movie moves like one giant promise kept.
2018|Cult Favorite|Hereditary|miniature houses on the table~telephone-pole shock that no one forgets~ceiling and corners in the dark~grief in the home turning into something worse|family-horror dread~disturbing imagery~slow-burn breakdown~cult devotion|Hereditary is remembered through a handful of images that landed hard and never really left. The house itself becomes a nerve center for the whole nightmare.
2018|Date Night|A Star Is Born|parking-lot and drag-bar meeting~Shallow rising on the stage~parking-garage and truck-stop intimacy~festival lights and backstage quiet|music-and-romance pull~star chemistry~big songs~weepy directness|A Star Is Born is remembered through the first meeting and Shallow taking over the stage. Bradley Cooper and Lady Gaga give the movie enough chemistry to carry every quieter scene too.
2018|Underrated|Widows|planning the job in borrowed rooms~Van crossing Chicago with a full life inside her face~campaign money and crime tying together~heist night with nerves stretched tight|heist tension~great ensemble~city-politics undercurrent~tough-minded style|Widows keeps getting stronger because the heist sits inside a much bigger city story. Viola Davis and the Chicago setting give the whole thing extra weight.
2018|The One That Grows on You|First Man|moon-landing sequence in near silence~training and test flights risking everything~family scenes holding the cost close~dusty lunar surface finally opening up|intimate epic~quiet awe~performance restraint~technical immersion|First Man lands harder later because the movie stays so close to one family and one pilot even when history gets huge. The moon sequence is what people remember first, but the silence around it matters just as much.
2018|Crowd Favorite|Crazy Rich Asians|wedding in the flooded aisle~Singapore parties with impossible money~mahjong scene changing the whole tone~family house and gardens full of pressure|rom-com glamour~big ensemble charm~luxury spectacle~crowd-pleasing warmth|Crazy Rich Asians is remembered through the wedding and the parties, but the mahjong scene is the one people bring up once the sparkle fades. The movie had enough style to feel like an event.
2018|After Midnight|The Favourite|duck-race absurdity~palace corridors and candlelight~letters and scheming in private rooms~dance floor turning the whole period piece sideways|wicked humor~performance battles~palace intrigue~stylized period energy|The Favourite is remembered through candlelit hallways, sharp dialogue, and a dance scene nobody expected from that setting. Olivia Colman, Emma Stone, and Rachel Weisz keep every scene alive.
"""

EXTRA_CATALOG_TEXT += """
# 2019
2019|Crowd Favorite|Parasite|family easing into the rich house one step at a time~ram-don and the storm~birthday-party tension building in broad daylight~stairs turning into the whole shape of the story|social-thriller bite~surgical pacing~crowd reaction power~sharp visual design|Parasite is remembered through the house, the stairs, and the way each new room changes the movie. The tension never really loosens once the family starts getting inside.
2019|After Midnight|Marriage Story|big apartment argument~lawyers turning private pain into process~theater-life routines in New York and Los Angeles~Charlie and Nicole trying to stay decent through the damage|relationship drama~actor showcase~painful honesty~lived-in detail|Marriage Story is remembered through one or two scenes that hit like a truck, especially the apartment fight. Adam Driver and Scarlett Johansson keep the whole movie painfully close.
2019|Big Screen Moment|Avengers: Endgame|time-heist team-ups~final portal sequence~quiet cabin and lakeside grief~battlefield packed with nearly everybody|franchise payoff~massive scale~crowd-cheer energy~event-movie spectacle|The portals scene is the image almost everyone goes to first, and Endgame knew it had earned that reaction. The movie played like a full-pop-culture finish line.
2019|Rewatchable|Knives Out|reading the will in the living room~Marta and Harlan's nighttime routine~the family circling each other in the mansion~detective monologues with the case still shifting|mystery fun~ensemble comedy~great pacing~repeat-watch pleasure|Knives Out is remembered through the house, the family fights, and Daniel Craig turning every explanation into a performance. The whole movie is built for another spin.
2019|Cult Favorite|Uncut Gems|Diamond District under neon and pressure~opening with the Celtics game looming over everything~auction-room panic~Howard running from one bad choice to the next|nervy energy~street-level chaos~cult intensity~anxiety by design|Uncut Gems is remembered through motion, noise, and the feeling that Howard never has one quiet second. The movie turns stress into its whole operating system.
2019|Date Night|Little Women|March sisters in the attic and by the fire~Jo and Laurie running through youth and change~New York and Paris letters crossing~Amy and Jo both finding their place in different rooms|warm literary comfort~ensemble strength~romantic and family pull~rewatchable coziness|Little Women is remembered through the house, the sisters, and all that winter light around the March family. The movie feels lively enough that the old story seems new again.
2019|Underrated|Ford v Ferrari|Shelby and Miles building the car in the shop~test runs shaking the frame~Le Mans day-night grind~pit-lane arguments turning personal|racing immersion~great two-hander~mechanical detail~crowd-pleasing momentum|Ford v Ferrari is remembered through engines, stopwatches, and Christian Bale throwing himself into every turn. The race footage is huge, but the garage scenes matter just as much.
2019|The One That Grows on You|Once Upon a Time in Hollywood|driving through Los Angeles at magic hour~Rick on the western set~Cliff at Spahn Ranch with the air going bad~movie-night and TV-night drifting across the city|hangout rhythm~period texture~star chemistry~sunset melancholy|Once Upon a Time in Hollywood sticks because the city, the radio, and the idle conversation feel so lived in. The ranch scene is the one people mention once the rest of the atmosphere settles.
2019|Crowd Favorite|1917|trench run to the front~flare-lit ruins at night~river carrying the soldier forward~crossing the battlefield with the score rising|war-film immersion~single-shot illusion~big-screen urgency~emotional drive|1917 is remembered through motion, especially in the trenches and the night-lit ruins. The movie feels like one long breath that never quite comes back out.
2019|After Midnight|Us|tunnel and funhouse echoes from childhood~red-suited doubles at the end of the driveway~family on the lake trying to stay ahead~living room turned into a stage for the confrontation|home-invasion fear~double-image horror~Jordan Peele tension~memorable iconography|Us is remembered through those red suits and the image of doubles standing outside the house. The movie keeps its whole nightmare close to familiar family space.

# 2020
2020|Crowd Favorite|Soul|Joe in the jazz club dream~Great Before orientation~body-switch trouble in New York~tiny everyday moments suddenly looking enormous|family appeal~big ideas made accessible~music-world energy~emotional clarity|Soul is remembered through jazz, blue beyond-space imagery, and the way ordinary life starts glowing by the end. Pixar made a movie about little moments and somehow made it feel huge.
2020|After Midnight|Nomadland|van life on open roads~Amazon warehouse and seasonal work~campfire conversations with other nomads~desert and badlands stretching out in all directions|quiet realism~open-road melancholy~human-scale storytelling~landscape beauty|Nomadland is remembered through roads, camps, and Frances McDormand sitting inside a life that keeps moving. The space around her is part of the feeling.
2020|Big Screen Moment|Tenet|opera-house opening confusion~highway truck sequence~inverted fight in the hallway~temporal pincer movement turning the battlefield inside out|big-concept action~spectacle first~Nolan scale~puzzle-box energy|Tenet is remembered through the highway sequence and the moments when time itself starts moving wrong. The movie was built to make people sit up and try to catch it.
2020|Rewatchable|Palm Springs|wedding-day loop beginning again~pool float drifting under the desert sun~cave revelation changing the rules~party scenes turning looser every time around|rom-com loop fun~easy chemistry~desert-vacation mood~great replay value|Palm Springs is remembered through the pool, the wedding, and the way both leads settle into the loop with very different energy. The movie keeps things breezy without losing its heart.
2020|Cult Favorite|The Invisible Man|empty room framed like a threat~restaurant shock in full public view~home-security dread at night~attic and paint tricks turning paranoia visible|modern horror tension~single-woman perspective~smart scare design~cult conversation starter|The Invisible Man keeps people looking at empty corners and waiting for them to move. The restaurant scene is the one most viewers never stop talking about.
2020|Date Night|Emma.|country-house introductions with too much confidence~dance and hand touch at the assembly~picnic day going badly in a very proper way~snow and carriage scenes with feelings finally out in the open|period-romance sparkle~comic precision~beautiful production design~light-footed charm|Emma. is remembered through colors, glances, and one or two moments where the room suddenly changes temperature. The movie has a crisp little bounce to it.
2020|Underrated|Sound of Metal|drum performance before the silence hits~Ruben at the deaf community house~writing and carpentry taking the place of noise~city streets sounding unfamiliar after everything shifts|sensory immersion~performance power~identity crisis~quiet emotional force|Sound of Metal is remembered through sound dropping away and the way the world changes with it. Riz Ahmed carries the whole movie through confusion and stubbornness.
2020|The One That Grows on You|Minari|family arriving on the Arkansas land~children exploring the fields and creek~grandmother changing the house in small ways~rain, fire, and hard work reshaping the farm|family focus~rural atmosphere~gentle humor~lingering emotion|Minari gets stronger later because the farm and the family routines feel so specific. The creek, the trailer home, and the grandmother are the memories most people hold onto.
2020|Crowd Favorite|The Trial of the Chicago 7|courtroom eruptions~convention-floor chaos in flashback~witnesses turning the room~closing statement landing with the whole place listening|talk-driven tension~ensemble energy~historical immediacy~crowd-pleasing pace|The Trial of the Chicago 7 moves fast enough that the courtroom rarely sits still for long. The clashes between the activists and the judge are what people tend to remember first.
2020|After Midnight|Promising Young Woman|coffee-shop and club setups repeating with a purpose~neon-night revenge mood~old classmate encounters growing more loaded~past trauma hanging over every bright pop song|stylized revenge drama~dark humor edge~pop-color design~unsettling momentum|Promising Young Woman is remembered through candy colors and scenes that keep turning much darker than they look. Carey Mulligan gives the movie its whole stare.

# 2021
2021|Crowd Favorite|Dune|arrival on Arrakis~ornithopters lifting over the desert~sandworm reveal at full scale~voice training and visions pushing the world wider|big-screen sci-fi~desert grandeur~franchise-launch force~visual immersion|The first Arrakis landing and the sandworm reveal are the images most people pull up first. Dune gave scale back its full weight.
2021|After Midnight|The Power of the Dog|ranch-house silence cutting through every meal~rope work and paper flowers~banjo challenge in the room~open land hiding very private wars|slow-burn tension~performance showcase~western unease~psychological pressure|The Power of the Dog is remembered through small gestures and the way the ranch never feels restful. Benedict Cumberbatch's presence fills the whole landscape.
2021|Big Screen Moment|Spider-Man: No Way Home|bridge fight with the returning villain~multiverse tears over the skyline~three Spider-Men sharing the frame~Statue of Liberty turned into a giant battleground|fan-payoff thrill~crowd-reaction energy~big-screen comic-book fun~franchise crossover spectacle|No Way Home is remembered through reveals people wanted to experience in a full room. The bridge, the Statue of Liberty, and that team-up shot are the main memory anchors.
2021|Rewatchable|No Time to Die|matera chase across stone streets~Cuba party turning into a field of bodies~forest and fog set pieces~Bond and Paloma lifting the whole movie for a stretch|Bond spectacle~franchise callback energy~stylish action~easy replay scenes|No Time to Die gives people a few big sequences they keep going back to, especially Matera and Cuba. The movie knows how to stage star entrances.
2021|Cult Favorite|Malignant|jail-cell chaos~police station turning into a nightmare~Seattle underground reveal~murder scenes that lean hard into the ridiculous|go-for-broke horror~camp energy~wild action-horror mix~cult-audience delight|Malignant became a cult favorite because it commits to its craziest ideas without blinking. The jail and police-station scenes are what most viewers bring up first.
2021|Date Night|Licorice Pizza|waterbed hustle~pinball and storefront wandering~truck rolling backward down the hill~San Fernando Valley running on pure young energy|sunny nostalgia~romantic drift~hangout charm~music-scene warmth|Licorice Pizza is remembered through movement and mood more than plot. The truck sequence and all that Valley wandering are the pieces that stay behind.
2021|Underrated|The Worst Person in the World|party scene that reshapes the whole movie~city frozen while she runs to the café~Oslo apartments and late-night talks~new love and old mistakes crowding the same year|romantic restlessness~modern-city mood~sharp humor~emotional honesty|The Worst Person in the World gets remembered through that frozen-city run and the feeling that a whole life can change over coffee. Oslo gives the movie a bright, restless energy.
2021|The One That Grows on You|CODA|fishing-boat mornings~choir rehearsal and audition nerves~family discovering what Ruby's voice means outside the house~kitchen and truck scenes carrying the emotional load|family warmth~music-and-home balance~crowd-pleasing emotion~gentle humor|CODA settles in because the family scenes feel so lived in and funny before the emotion lands. The fishing boat and the audition are what people usually remember first.
2021|Crowd Favorite|West Side Story|gym dance lights and movement~Gee, Officer Krupke and the street energy around it~Tonight unfolding across the city~fire-escape and warehouse tension turning tragic|musical force~fresh staging~big ensemble energy~famous songs revived|West Side Story is remembered through the dancing and camera movement almost immediately. Spielberg gave the familiar numbers enough sweep to feel new again.
2021|After Midnight|Drive My Car|red Saab moving through long roads~festival rehearsal room with actors in many languages~conversations in the car that take their time~the play and the grief slowly finding each other|patient storytelling~performance layers~quiet emotional depth~road-movie calm|Drive My Car is remembered through the red car and the rehearsal room as much as any plot turn. The movie lets conversation do the heavy work.

# 2022
2022|Crowd Favorite|Top Gun: Maverick|training runs through the canyon~beach-football hangout~first impossible test flight~mission sequence with everybody in the air at once|legacy-sequel payoff~aerial spectacle~star charisma~crowd-cheer energy|Top Gun: Maverick is remembered through the training flights and the mission in full motion. The movie had the kind of full-room reaction that is hard to fake.
2022|After Midnight|The Banshees of Inisherin|friendship ending on the road by the sea~pub scenes going cold in a hurry~fingers and fiddles turning the feud uglier~island quiet making everything sharper|dark comedy~Irish atmosphere~actor showcase~sadness under the absurdity|The Banshees of Inisherin is remembered through talk in the pub and long walks where nothing gets better. The island setting gives every silence extra weight.
2022|Big Screen Moment|Avatar: The Way of Water|sea-clan arrival~underwater rides and creatures~sinking-ship chaos~family under pressure across every horizon|ocean-world spectacle~big-screen immersion~family stakes~visual grandeur|The Way of Water is remembered through underwater motion and the sheer amount of screen-filling detail. The sinking-ship stretch is the scene most people jump to after the first viewing.
2022|Rewatchable|Glass Onion: A Knives Out Mystery|arrival on the private island~murder-mystery weekend turning into a very different game~glass structure under the sun~Daniel Craig guiding the room with a grin|mystery comfort~ensemble comedy~colorful setting~easy replay pull|Glass Onion keeps the same thing people liked about Knives Out and moves it someplace brighter and louder. The island and the ensemble games are the main memory set.
2022|Cult Favorite|Nope|horse-ranch routine under a strange sky~cloud that should not stay in one place~nighttime theme-park detour~spectacle turned back on the audience|big-idea horror~western-sci-fi mix~IMAX-friendly imagery~cult discussion fuel|Nope is remembered through the sky, the cloud, and the whole idea of spectacle watching back. Jordan Peele gave the movie a handful of images that people keep unpacking.
2022|Date Night|Decision to Leave|mountain-climb investigation~text messages and stakeouts becoming intimate~sea and fog turning the mystery softer and stranger~police rooms lit like private confessionals|romantic noir mood~mystery pull~beautiful camerawork~late-night atmosphere|Decision to Leave is remembered through glances, phones, and fog more than any one explanation. The whole movie feels like a case file turning romantic by accident.
2022|Underrated|Guillermo del Toro's Pinocchio|wooden puppet first taking life~musical-fantasy turns under candlelight~war and circus imagery crossing in one world~father and son thread holding the whole story|handmade artistry~dark fairy-tale feeling~family emotion~visual richness|Del Toro's Pinocchio is remembered through its tactile look and the way the old story gets a little darker without losing its heart. The animation itself is half the memory.
2022|The One That Grows on You|The Batman|rain-soaked Gotham introduction~bat-signal and hallway footsteps~car chase in the fire and wreckage~funeral and arena plots stretching the citywide mood|moody detective feel~gothic city design~slow-burn hero turn~strong atmosphere|The Batman settles in because Gotham feels so complete and the detective angle keeps pulling stronger on a second look. The hallway entrance and the car chase are the images people hold first.
2022|Crowd Favorite|Everything Everywhere All at Once|IRS office spiraling into multiverse chaos~fanny-pack fight nobody expected~rocks on the cliff in absolute silence~hallway and parking-lot kindness breaking through the noise|maximal imagination~family emotion~comic invention~crowd-pleasing originality|The googly eyes, the fanny-pack fight, and the rock scene are enough to make Everything Everywhere instantly recognizable. The movie earns its chaos by keeping one family at the center.
2022|After Midnight|Tár|classroom debate turning electric~rehearsal-room authority on full display~Berlin apartments and backstage corridors~conductor's world slipping out of her control by degrees|performance-driven~psychological chill~art-world tension~controlled pacing|Tár is remembered through rooms where status and pressure sit right on top of each other. Cate Blanchett gives the movie a steel edge that stays with people.

# 2023
2023|Crowd Favorite|Oppenheimer|Trinity test countdown~opening with particles and fear~black-and-white hearing rooms~Los Alamos life under enormous stakes|event-movie weight~historical scale~performance power~big-screen intensity|Oppenheimer is remembered through the countdown and the blast, but the hearing rooms stay with people too. The movie feels like history and panic pressed together.
2023|After Midnight|The Zone of Interest|garden and house routines beside the wall~sound doing half the horror~pool and patio scenes turned sickening by what surrounds them~domestic order refusing to acknowledge the truth next door|quiet horror~formal control~historical dread~haunting sound design|The Zone of Interest is remembered through what you hear around ordinary domestic scenes. The wall, the garden, and the refusal to look are the whole movie's nightmare.
2023|Big Screen Moment|Barbie|pink dreamhouse reveal~dance-party opener~trip into the real world~boardroom and bus-stop scenes turning the joke into something larger|pop-color spectacle~crowd-event energy~sharp comedy~big cultural footprint|Barbie is remembered through pure image almost immediately, from the dreamhouse to the rollerblades to the all-pink world. The movie had enough jokes and feeling to turn a toy into a full event.
2023|Rewatchable|Spider-Man: Across the Spider-Verse|Gwen's watercolor world~Spider-Society headquarters~Mumbattan action with the city folding around the chase~Miles running through a dozen styles at once|animation fireworks~superhero momentum~repeat-watch density~franchise excitement|Across the Spider-Verse moves so fast and looks so different from scene to scene that people keep finding new details in it. The Spider-Society and Mumbattan are the big memory anchors.
2023|Cult Favorite|Poor Things|Baxter house in bright odd colors~European travel growing stranger by the stop~dancing and dining rooms turned inside out~Bella learning the world with no interest in doing it quietly|wild visual imagination~offbeat humor~cult-cinema energy~fearless lead turn|Poor Things is remembered through design, costume, and Emma Stone walking through the whole movie like normal rules never existed. The picture feels handmade and unruly in the best way.
2023|Date Night|Past Lives|childhood connection in Seoul and online again years later~New York walks and quiet bars~ferry and street scenes at the end of the visit~three people sharing one night with a lot underneath it|romantic melancholy~city intimacy~gentle pacing~emotional clarity|Past Lives is remembered through conversation, walking, and one visit that feels both huge and very small. The movie keeps everything soft-spoken and still lands hard.
2023|Underrated|The Holdovers|snowed-in campus over the holiday break~history teacher and student circling each other warily~kitchen and dorm routines turning into companionship~Boston trip giving the whole movie a little more room|winter comfort~character chemistry~sad-funny balance~holiday rewatch potential|The Holdovers is remembered through the campus in winter and the chemistry among its three leads. The movie feels cozy until the hurt underneath starts coming through.
2023|The One That Grows on You|Killers of the Flower Moon|wedding and oil-money pageantry~Osage family gatherings under quiet threat~courtroom and investigation material arriving late~Oklahoma towns carrying a buried dread|historical gravity~slow-burn crime drama~performance focus~lingering weight|Killers of the Flower Moon gets heavier once the scale of what is happening settles in. The family gatherings and all that calm surface are the pieces that keep sticking.
2023|Crowd Favorite|John Wick: Chapter 4|Arc de Triomphe roundabout sequence~Osaka hotel neon and swords~stair climb that keeps getting interrupted~desert duel and old-code mythmaking|action spectacle~franchise confidence~stunt precision~crowd-pleasing rhythm|John Wick: Chapter 4 is remembered through set pieces, starting with Osaka and the Arc de Triomphe. The movie knows the audience came to see pure action craft and keeps delivering it.
2023|After Midnight|Anatomy of a Fall|house and mountain setting under suspicion~courtroom cross-examination turning intimate~recording from the marriage laid bare~dog and child carrying pieces of the truth|courtroom tension~relationship mystery~actor showcase~cold precision|Anatomy of a Fall is remembered through the courtroom and the way a marriage gets dissected in public. The snowy setting and Sandra Huller's performance keep the whole movie tense.

# 2024
2024|Crowd Favorite|Dune: Part Two|worm ride across the open desert~arena fight in black and white~southern temples and gathering war energy~sandstorms and prophecy filling the screen|desert spectacle~franchise escalation~big-screen immersion~mythic intensity|Dune: Part Two is remembered through scale almost immediately, especially the worm ride and the black-and-white arena. The movie feels like the whole world got louder and more dangerous.
2024|After Midnight|The Substance|mirror and body ritual scenes~studio and apartment spaces turning hostile~television-performance pressure~body-horror set pieces nobody forgets|satirical horror~shock imagery~star performance~midnight-movie energy|The Substance is remembered through its transformation scenes and the way glamour turns ugly right in front of the audience. The movie has the kind of imagery people talk around for days.
2024|Big Screen Moment|Wicked|Defying Gravity launch into the air~Shiz University arrival~Emerald City spectacle~Elphaba and Glinda finding the center of the story together|musical event scale~beloved songs~fantasy production design~crowd-singalong appeal|Wicked is remembered through the songs everybody already knew were coming, especially Defying Gravity. The scale and color give the whole adaptation a full-event feeling.
2024|Rewatchable|Hit Man|fake identities at the diner and bar~car and surveillance setups~romance sliding into criminal playacting~Glen Powell changing modes every few scenes|star charm~crime-rom-com snap~high-concept fun~easy replay value|Hit Man is remembered through the disguises and the way Glen Powell keeps shifting the temperature of every scene. The movie moves lightly even when the stakes start getting strange.
2024|Cult Favorite|Longlegs|serial-killer clues scattered through empty rooms~nervy visits to old houses~telephone and audio fragments turning everything colder~Maika Monroe carrying the whole investigation in a trance-like state|creeping dread~serial-killer mood~cult-horror pull~sticky atmosphere|Longlegs is remembered through mood first, especially the empty houses and all that brittle silence. The movie feels like bad news already hanging in the walls.
2024|Date Night|Challengers|tennis triangle set in motion~locker-room and hotel-room tension~courtside rivalry turning personal~match points carrying years of history between the three leads|romantic tension~sports-drama heat~stylish energy~star chemistry|Challengers is remembered through sweat, eye contact, and the way every match feels like a conversation nobody is having out loud. The triangle is the whole engine.
2024|Underrated|A Real Pain|family trip across Poland~train rides and small arguments~tour-group dynamics turning unexpectedly personal~grief and humor sitting in the same scene|road-trip intimacy~sad-funny tone~strong two-hander~human-scale emotion|A Real Pain is remembered through travel, talk, and two cousins who keep exposing each other's weak spots. The movie stays small and gets a lot from that choice.
2024|The One That Grows on You|The Wild Robot|robot waking alone on the island~animals slowly accepting Roz~storm and migration sequences widening the scale~quiet parenting beats that sneak up emotionally|family animation~nature-world beauty~gentle humor~unexpected heart|The Wild Robot gets stronger once the island and animal world settle into memory. Roz's awkward beginning and the softer parenting moments are what tend to last.
2024|Crowd Favorite|Inside Out 2|new emotions flooding headquarters~panic attack visualized in full motion~Riley on the hockey floor under pressure~core sense of self getting rebuilt in the middle of the storm|family appeal~emotional clarity~big sequel energy~crowd connection|Inside Out 2 is remembered through the new emotions barging into headquarters and the pressure-cooker hockey moments. The movie found another clean visual language for feelings people already knew.
2024|After Midnight|Civil War|opening unrest on ordinary streets~reporters traveling south through a country coming apart~sniper sequence in open daylight~Washington approach turning into full combat|war-correspondent tension~road-movie dread~visceral sound and image~unsettling immediacy|Civil War is remembered through the road trip, the press helmets, and the feeling that every checkpoint could go wrong in seconds. The movie keeps the audience close to people documenting the breakdown.
"""

CATALOG_TEXT += EXTRA_CATALOG_TEXT


def build_catalog() -> dict[int, list[dict]]:
    catalog: dict[int, list[dict]] = defaultdict(list)
    for raw in CATALOG_TEXT.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        year_s, category, title, moments_s, takeaways_s, booth = line.split("|", 5)
        year = int(year_s)
        catalog[year].append(
            entry(
                category=category,
                title=title,
                year=year,
                signature_moments=moments_s.split("~"),
                audience_takeaways=takeaways_s.split("~"),
                projection_booth=booth,
            )
        )
    return dict(catalog)


CATALOG = build_catalog()


def validate_year_block(year: int, picks: list[dict]) -> None:
    if len(picks) != 10:
        raise ValueError(f"{year}: expected 10 picks, found {len(picks)}")
    counts = Counter(pick["category"] for pick in picks)
    if any(count > 3 for count in counts.values()):
        raise ValueError(f"{year}: category used more than 3 times")
    for pick in picks:
        if pick["film"]["year"] != year:
            raise ValueError(f"{year}: film year mismatch for {pick['film']['title']}")
        if len(pick["signature_moments"]) != 4:
            raise ValueError(f"{year}: wrong signature moment count for {pick['film']['title']}")
        if len(pick["audience_takeaways"]) != 4:
            raise ValueError(f"{year}: wrong takeaway count for {pick['film']['title']}")


def _apply_styles_to_picks(picks: list[dict], year: int, *, debug: bool = True) -> list[dict]:
    """Apply style modes to picks based on index. Skips entries that fail validation."""
    styled = []
    for i, pick in enumerate(picks):
        mode = STYLE_MODE_BY_INDEX.get(i, "A")
        styled_pick = generate_movie_entry(
            pick,
            mode,
            debug=debug,
            year=year,
            index=i,
        )
        if styled_pick is None:
            print(f"FAILED VALIDATION: {year} - {i}")
            continue
        styled.append(styled_pick)
    return styled


def _first_three_words(text: str) -> str:
    """First 3 words of first sentence (lowercase)."""
    words = re.findall(r"\w+", text.lower())
    return " ".join(words[:3]) if len(words) >= 3 else " ".join(words)


def audit_movie_memory(path: str | Path, start_year: int = 2000, end_year: int = 2024) -> dict:
    """
    Audit movie memory JSON for quality. Read-only.
    Returns audit results dict.
    """
    path = Path(path)
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)

    entries: list[tuple[int, int, str, str]] = []
    for year in range(start_year, end_year + 1):
        key = str(year)
        if key not in data:
            continue
        picks = data[key].get("picks", [])
        for i, pick in enumerate(picks):
            booth = pick.get("projection_booth", "")
            mode = MODE_NAMES.get(STYLE_MODE_BY_INDEX.get(i, "A"), "projection_booth")
            entries.append((year, i, mode, booth))

    total = len(entries)
    if total == 0:
        return {"total": 0, "entries": []}

    mode_counts: dict[str, int] = Counter(mode for _y, _i, mode, _b in entries)
    mode_pcts = {m: (c / total * 100) for m, c in mode_counts.items()}

    opening_counts: Counter[str] = Counter()
    for _y, _i, _m, booth in entries:
        opening_counts[_first_three_words(booth)] += 1
    threshold = max(1, int(total * 0.05))
    opening_repeats = [(phrase, c) for phrase, c in opening_counts.most_common() if c > threshold]

    banned_violations: list[str] = []
    for _y, _i, _m, booth in entries:
        lowered = booth.lower()
        for phrase in BANNED_PHRASES:
            if phrase in lowered:
                banned_violations.append(f"{booth[:80]}...")
                break

    sent_counts: Counter[int] = Counter()
    for _y, _i, _m, booth in entries:
        n = len(_sentences(booth))
        sent_counts[min(n, 3) if n >= 3 else n] += 1
    sent_1 = sent_counts.get(1, 0) / total * 100
    sent_2 = sent_counts.get(2, 0) / total * 100
    sent_3p = sum(c for k, c in sent_counts.items() if k >= 3) / total * 100

    memory_recall_entries = [(y, i, b) for y, i, m, b in entries if m == "memory_recall"]
    scene_indicators = ("scene", "moment", "sequence", "opening", "ending", "image", "stays")
    proper_noun = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b")
    memory_pass = 0
    for _y, _i, booth in memory_recall_entries:
        has_scene = any(w in booth.lower() for w in scene_indicators)
        has_proper = bool(proper_noun.search(booth))
        if has_scene or has_proper:
            memory_pass += 1
    memory_pct = (memory_pass / len(memory_recall_entries) * 100) if memory_recall_entries else 0

    return {
        "total": total,
        "entries": entries,
        "mode_counts": mode_counts,
        "mode_pcts": mode_pcts,
        "opening_repeats": opening_repeats,
        "banned_count": len(banned_violations),
        "banned_examples": banned_violations[:5],
        "sent_1": sent_1,
        "sent_2": sent_2,
        "sent_3p": sent_3p,
        "memory_recall_total": len(memory_recall_entries),
        "memory_pass": memory_pass,
        "memory_pct": memory_pct,
    }


def _print_audit_report(result: dict, start_year: int = 2000, end_year: int = 2024) -> None:
    """Print audit report to stdout."""
    if result["total"] == 0:
        print(f"=== MOVIE MEMORY AUDIT ({start_year}–{end_year}) ===\nNo entries found.\n")
        return

    total = result["total"]
    print(f"\n=== MOVIE MEMORY AUDIT ({start_year}–{end_year}) ===\n")
    print("Mode Distribution:")
    for mode in ("projection_booth", "memory_recall", "critic_lite", "hybrid_A_C", "hybrid_A_B"):
        c = result["mode_counts"].get(mode, 0)
        p = result["mode_pcts"].get(mode, 0)
        print(f"  {mode}: {c} ({p:.1f}%)")

    print("\nOpening Phrase Repeats:")
    if result["opening_repeats"]:
        for phrase, c in result["opening_repeats"]:
            print(f'  "{phrase}": {c} occurrences (FLAG)')
    else:
        print("  None above 5% threshold")

    print("\nBanned Phrase Violations:")
    print(f"  Count: {result['banned_count']}")
    if result["banned_examples"]:
        print("  Examples:")
        for ex in result["banned_examples"]:
            print(f"    - {ex}")
    else:
        print("  None found")

    print("\nSentence Structure:")
    print(f"  1 sentence: {result['sent_1']:.1f}%")
    print(f"  2 sentences: {result['sent_2']:.1f}%")
    print(f"  3+: {result['sent_3p']:.1f}%")

    print("\nMemory Recall Quality:")
    print(f"  {result['memory_pct']:.1f}% contain specific references")

    print("\n====================================\n")


def run_builder(
    *,
    reprocess: bool = False,
    debug: bool = True,
    start_year: int = START_YEAR,
    end_year: int = END_YEAR,
) -> None:
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    if SOURCE.exists():
        with SOURCE.open(encoding="utf-8") as fh:
            data = json.load(fh)
    else:
        data = {}

    updated = {str(year): data[str(year)] for year in sorted(int(k) for k in data)}

    for year in range(start_year, end_year + 1):
        key = str(year)
        picks = CATALOG.get(year)
        if not picks:
            if key in data:
                continue
            raise ValueError(f"No catalog data for {year}")

        if key in data and not reprocess:
            print(f"Skipped: {year}")
            continue

        validate_year_block(year, picks)
        styled_picks = _apply_styles_to_picks(picks, year, debug=debug)
        updated[key] = {"year": year, "picks": styled_picks}
        print(f"Added: {year}" if key not in data else f"Reprocessed: {year}")

    ordered = {str(year): updated[str(year)] for year in sorted(int(k) for k in updated)}
    serialized = json.dumps(ordered, indent=2, ensure_ascii=False) + "\n"
    validated = json.loads(serialized)
    if not isinstance(validated, dict):
        raise ValueError("Serialized JSON is not a dict")
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(serialized, encoding="utf-8")
    OUTPUT.replace(SOURCE)
    print("RetroVerse movie memory build complete")


def _run_projection_booth_demo() -> None:
    """Demo: full page JSON including cult_classic for one year."""
    year = 1998
    page = build_projection_booth_page(year, debug=True)
    print("\n--- Full page JSON ---")
    print(json.dumps(page, indent=2, ensure_ascii=False))
    if page.get("cult_classic"):
        cc = page["cult_classic"]
        print(f"\n--- Cult Classic example ---\nLabel: {cc['label']}\nTitle: {cc['title']}\nText: {cc['text']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build RetroVerse movie memory dataset.")
    parser.add_argument(
        "--reprocess",
        action="store_true",
        help="Re-apply style modes to all years (overwrites existing entries).",
    )
    parser.add_argument(
        "--no-debug",
        action="store_true",
        help="Disable YEAR - INDEX - MODE debug output.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=START_YEAR,
        metavar="YEAR",
        help=f"Start year (default: {START_YEAR}).",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=END_YEAR,
        metavar="YEAR",
        help=f"End year (default: {END_YEAR}).",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Run generation for 2000–2024 and audit results.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Show 3-film demo of unified projection booth text.",
    )
    parser.add_argument(
        "--movies-charts",
        action="store_true",
        help="Show Movies Charts page JSON.",
    )
    args = parser.parse_args()

    if args.movies_charts:
        page = build_movies_charts_page(1986, debug=True)
        print("\n--- Full page JSON ---")
        print(json.dumps(page, indent=2, ensure_ascii=False))
        return

    if args.demo:
        _run_projection_booth_demo()
        return

    if args.audit:
        print("Running generation (2000–2024)…")
        run_builder(
            reprocess=False,
            debug=True,
            start_year=2000,
            end_year=2024,
        )
        print("\nRunning audit…")
        result = audit_movie_memory(SOURCE, start_year=2000, end_year=2024)
        _print_audit_report(result, start_year=2000, end_year=2024)
        entries = result.get("entries", [])
        if entries:
            with SOURCE.open(encoding="utf-8") as fh:
                data = json.load(fh)
            by_mode: dict[str, list] = defaultdict(list)
            for y, i, m, b in entries:
                key = str(y)
                title = "?"
                if key in data and i < len(data[key].get("picks", [])):
                    title = data[key]["picks"][i].get("film", {}).get("title", "?")
                by_mode[m].append((y, title, b))
            print("Sample entries (3 modes):\n")
            for mode in ("projection_booth", "memory_recall", "critic_lite"):
                if mode in by_mode and by_mode[mode]:
                    y, title, b = by_mode[mode][0]
                    print(f"[{mode}] {y} {title}: {b[:70]}…\n")
    else:
        run_builder(
            reprocess=args.reprocess,
            debug=not args.no_debug,
            start_year=args.start,
            end_year=args.end,
        )


if __name__ == "__main__":
    main()
