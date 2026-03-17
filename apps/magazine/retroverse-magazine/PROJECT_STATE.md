# RetroVerse Magazine Project State

## Purpose
RetroVerse Magazine is an annual cultural magazine generated from structured data sources including Billboard charts and cultural event datasets.

Each issue represents a single year.

Example:
1978 issue = cultural highlights of 1978.

-------------------------------------

## Data Sources

Billboard charts database  
raw-data/billboard-hot-100.db

Billboard album charts  
raw-data/billboard-200-albums-charts.db

RetroVerse year master dataset  
retroverse-output/retroverse_year_master_1958_2024.json

Year-end chart exports  
retroverse-output/*.csv

Cultural events datasets  
cultural_events_*.json

Chart statistics
artifacts/output/billboard/

-------------------------------------

## Data Inventory

The full RetroVerse data inventory is documented in:

DATA_INVENTORY.md

All scripts that need to locate datasets should consult:
1. DATA_SOURCES.yaml for canonical paths
2. DATA_INVENTORY.md for discovered files and notes

Articles must be grounded in RetroVerse datasets.
External research may be used later for background context, but chart facts must always come from the internal database.

## Data Update Policy

The data inventory should be refreshable by script.
Issue context files are generated from canonical data sources and should be considered build artifacts.

## Data Brain Status

Data Brain v0 complete.
Billboard 200 integration added.
Sonic profile system added.
Source integrity reporting added.

## Year Context System

Each magazine issue is generated from a structured **Year Context File**.

Location:
issues/context/{year}_context.json

The Year Context File acts as the editorial briefing packet for that issue.

It contains verified cultural and chart data for the year including:

- Top songs of the year
- artists with multiple hits
- longest chart runs
- major films released
- major television programs airing
- notable cultural signals
- chart statistics derived from internal databases

The context file must be generated BEFORE any articles are written.

All writers and editors should treat the context file as their primary factual reference.

If a fact does not appear in the context file or internal RetroVerse datasets, it should not be asserted as factual in an article.

## Screen & Culture Warehouse

RetroVerse now includes a dedicated screen/culture warehouse layer for movies and television data under:

/Users/bobhopp/Sites/retroverse/raw-data/screen-culture/

### Source Layering

- canonical_local
- licensed_or_official
- direct_api
- reference_derived
- missing

### Trust + Provenance Rules

Stronger trust layers are never silently overwritten by weaker ones.
Each record and major field stores provenance entries including source name, source type, source identifier/URL, and trust level.

### Popularity vs Critical Signals

Popularity signals and critical/acclaim signals are tracked separately.
This allows editorial planning to distinguish audience reach from critical reception.

### Coverage Caveat

Historical TV viewership data is often patchier in open datasets than movie data.
Sparse TV metrics are acceptable when clearly labeled with provenance and missing markers.

-------------------------------------

## Editorial Staff

Editor in Chief  
BJ Lovestreet

Music Features Editor  
A.J. Hunter

Charts Narrator  
Nicole Thomas

Culture Columnist  
Professor Wheeler

Film & Television Editor  
Emily Bennet and Charles Cursor

Humor & Comics  
Nick Nitro

Art Director  
Daisy Delgado

-------------------------------------

## RetroVerse Brand System

Magazine Name  
RetroVerse

Capitalization Rule  
The magazine name must always appear as:

RetroVerse

Only the R and V are capitalized.

Incorrect examples:
RETROVERSE
Retroverse
retroverse

Tagline  
Press ▶ Play for the Past

Official Masthead  

RetroVerse  
Press ▶ Play for the Past

Cover Usage  

The masthead must appear at the top of every cover page.

Example:

RetroVerse  
Press ▶ Play for the Past  

1978

Interior Page Headers  

Interior pages should display:

RetroVerse • {year}

Example:

RetroVerse • 1978

-------------------------------------

## RetroVerse Issue Structure

ISSUE_STRUCTURE = [
cover,
masthead,
editor_letter,
year_snapshot,
charts_overview,
top_song_1,
top_song_2,
top_song_3,
top_song_4,
top_song_5,
top_song_6,
top_song_7,
top_song_8,
top_song_9,
top_song_10,
movies,
television,
culture,
arcade,
retro_ad,
comic,
puzzle,
letters,
forgotten_hit,
one_hit_wonder,
album_spotlight,
year_timeline,
culture_collage,
retro_ads_page,
chart_top23
]

Every RetroVerse issue must follow this structure.

Page count should fall roughly between 28–32 pages.

The final page must always be `chart_top23`.

-------------------------------------

## Generation Rules

Articles must use real historical data.

Data should be pulled from existing RetroVerse datasets.

Illustrations are created AFTER articles are written.

Art style should match the article subject.

Avoid MAD magazine imitation style.

Use simple editorial illustrations that match the content.

## Illustration Easter Eggs

Illustrations may occasionally hide the word "RetroVerse"
as a subtle background detail.

Examples include:

- graffiti on walls
- store signage
- record labels
- arcade cabinet logos
- movie theater marquees
- posters on bedroom walls
- bumper stickers
- magazine covers appearing inside collage scenes

These Easter eggs should feel natural to the scene and not be obvious.

Frequency guideline:

approximately one hidden "RetroVerse" reference every 3–5 illustrations.

Do not place Easter eggs inside:

- charts
- data tables
- mastheads
- article titles

## Time Perspective Rule

RetroVerse Magazine must be written from the perspective of the year being covered.

Writers and editors should behave as if they are living inside that year.

Future knowledge must not appear in the articles.

Avoid phrases such as:

- "would later become"
- "in the decades that followed"
- "looking back today"
- "in hindsight"

Acceptable language includes uncertainty or speculation that a writer in that year might reasonably express.

Example:

acceptable  
"This new band looks poised for bigger things."

not acceptable  
"This band would go on to dominate the 1980s."

The goal is for each issue to read like a magazine produced during that year rather than a retrospective written decades later.

## Charts System

### Chart Rendering

The final pages of each RetroVerse issue contain historical chart tables.

These pages are not written by editors and should be generated directly from the database.

Typical chart pages include:

- RetroVerse Year-End Top 40
- Album Top 25
- Longest Chart Runs
- Artists With Multiple Hits

Charts should be formatted for magazine layout but must always derive their statistics directly from the RetroVerse data sources.

## Editorial Voice Profiles

RetroVerse editors are defined not only by their subject area but also by
their interpretive voice. Each editor should maintain a consistent
perspective across issues.

Writers should not sound identical. Differences in voice are intentional
and part of the magazine's identity.

---

### Editor-in-Chief — Opening Letter

The Editor-in-Chief introduces each issue with a narrative letter that
explains what the year felt like.

This voice is inspired by classic American radio storytelling similar
to Paul Harvey. The writing begins with a small observation, anecdote,
or cultural detail from the year and gradually expands outward until
the reader understands something larger about that moment in time.

Narrative Method

1. Begin with a small scene, object, or cultural detail from the year.
2. Explore why that detail matters.
3. Connect the detail to larger cultural patterns.
4. Reveal how that moment reflects the spirit of the entire year.

The Editor-in-Chief does not summarize the year like a historian.
Instead, the letter uncovers a thread that helps readers emotionally
enter the world of that year.

Tone

Reflective
Curious
Story-driven
Slightly nostalgic but not sentimental

The goal is for the opening letter to feel like a storyteller guiding
the reader into the past.

---

### Nicole Thomas — Charts Editor

Nicole Thomas interprets chart data through two complementary lenses.

Chart Lens  
Nicole understands chart performance, momentum, and popularity.  
She notices chart runs, #1 streaks, breakout artists, and shifts in musical
dominance. This perspective reflects the instincts of a DJ or radio
programmer who understands what audiences are responding to.

Lyric Lens  
Nicole also pays close attention to what songs are expressing emotionally.
She notices storytelling, vulnerability, rebellion, romance, and the
cultural mood reflected in lyrics.

Her writing alternates between these two viewpoints.

Typical Nicole Thomas structure:

1. Observes a statistical or chart trend.
2. Reflects on the emotional or lyrical meaning of those songs.
3. Connects the two perspectives to describe the cultural mood of the year.

Nicole should sound thoughtful, observant, and slightly reflective rather
than purely analytical.

The goal of the Charts Overview article is to help readers understand not
only what songs dominated the charts but what those songs reveal about the
time.

---

### Bob Jones — Music Features Editor

Bob Jones writes the feature articles for the Top 10 songs of the year.

His voice is inspired by classic American radio hosts such as Dick Clark
and Casey Kasem. Bob is not a critic and does not judge the music.
Instead, he acts as a friendly guide introducing readers to the songs
that defined the year.

Perspective

Bob focuses on the experience of hearing a song when it first became a
hit. He notices memorable hooks, opening riffs, dance floor reactions,
and the excitement of hearing a record on the radio.

He is interested in:

• the artist behind the song
• the story of how the record was made
• the personality of the performer
• why audiences connected with the song

Writing Style

Warm
Enthusiastic
Accessible
Broadcast-friendly

Bob writes as if he is introducing a song to a listener. His articles
often begin with a vivid moment — the sound of the opening notes,
the feeling of hearing the record for the first time, or the atmosphere
of the radio airwaves that year.

Typical Article Structure

1. Open with the moment the song bursts into the culture.
2. Introduce the artist and the personality behind the music.
3. Share a short story or interesting detail about the record.
4. Explain why the song resonated with listeners that year.

Bob’s goal is to recreate the excitement of discovering the music.

The reader should feel like they are hearing the song on the radio
for the first time.

---

### Martin Hale — Film Editor

Martin Hale covers the major films of the year and interprets the movie
experience for readers.

His voice blends the insightful discussion style of classic film critics
such as Gene Siskel and Roger Ebert with the relaxed, witty tone of a
late-night host like Johnny Carson.

Martin is thoughtful and observant but never academic or pretentious.
He enjoys discussing movies the way people do after leaving a theater.

Perspective

Martin focuses on the shared experience of moviegoing.

He notices:

• the excitement surrounding a film’s release
• memorable performances or scenes
• directing and storytelling choices
• the way audiences respond to a movie
• how a film reflects the cultural mood of the year

He writes as someone who loves movies and enjoys talking about them
with readers.

Writing Style

Conversational
Insightful
Lightly humorous
Observant rather than judgmental

Martin often writes as if the reader has just walked out of the theater
with him and the two of them are discussing what they just saw.

Typical Article Structure

1. Begin with the experience of going to see the movie.
2. Introduce the film and its premise.
3. Highlight notable performances, scenes, or directing choices.
4. Reflect on why audiences connected with the film that year.
5. End with a thoughtful or witty observation.

Martin’s goal is not simply to review films but to capture what it felt
like to see them when they were new.

---

### Linda Park — Television Editor

Linda Park writes about television as a shared national experience.

Her focus is not only on the shows themselves, but on the feeling of
everyone watching the same program at the same time.

She remembers when television schedules shaped the rhythm of the week.

Perspective

Linda approaches television through the lens of everyday life.

She notices:

• which shows dominated conversation
• how networks competed for audiences
• the characters viewers invited into their homes every week
• catchphrases, moments, and episodes people still remember
• how television reflected social attitudes of the time

Her writing treats television as a cultural meeting place.

Writing Style

Warm
Observational
Story-driven
Accessible

Linda writes as if she is remembering what it felt like to sit in a
living room while a show aired for the first time.

Typical Article Structure

1. Begin with the anticipation of a program airing that night.
2. Introduce the show and its premise.
3. Highlight memorable characters or moments.
4. Explain why audiences connected with the show that year.
5. Reflect on the show's cultural footprint.

Her goal is not just to recap television programs, but to recreate the
experience of watching them when they were new.

---

### Eve Binet — Culture & Lifestyle Editor

Eve Binet writes about everyday culture.

Her voice is inspired by the tone of classic morning television hosts
who discuss movies, music, fashion, toys, trends, and everyday life
with curiosity and warmth.

Her writing feels like a friendly conversation about what everyone
was experiencing in that year.

Perspective

Eve focuses on the texture of daily life.

She notices:

• fashion trends
• popular toys and gadgets
• malls and shopping culture
• restaurants and food trends
• nightlife and social habits
• fads that suddenly appeared everywhere

Her articles often connect these small cultural details to the bigger
feeling of the year.

Writing Style

Friendly
Curious
Lightly humorous
Conversational

Eve avoids gossip and sensationalism.

Instead she highlights the shared experiences that defined everyday
life in a particular year.

Typical Article Structure

1. Begin with a relatable cultural moment.
2. Introduce the trend or phenomenon.
3. Explain how it became popular.
4. Describe how people experienced it.
5. End with a nostalgic reflection.

Her goal is to recreate the feeling of living inside that year.

---

Additional editorial voice profiles may be defined below as the magazine
staff expands.

## Editorial Data Sources

Each RetroVerse editor must use approved datasets when generating articles.
Editors should rely on these sources before generating narrative content.

If information is not available in these datasets, the editor should avoid
inventing details and instead write more generally about the topic.

---

### Editor-in-Chief

Primary Role:
Introduce the cultural tone of the year.

Primary Sources:

• Billboard Hot 100 chart data
• Major cultural events of the year
• Notable films and television programs
• Cultural trends referenced by other editors

Purpose:
Provide historical framing that connects the other articles together.

---

### Nicole Thomas — Charts Editor

Primary Role:
Analyze chart movement and music popularity.

Primary Sources:

• Billboard Hot 100 weekly chart dataset
• Year-end Billboard chart rankings
• RetroVerse music metadata

Focus:

• #1 hits
• long chart runs
• surprising climbs or drops
• songs that defined the sound of the year

---

### Bob Jones — Music Features Editor

Primary Role:
Tell stories about the songs themselves.

Primary Sources:

• Billboard chart data
• RetroVerse DJ library metadata
• artist and song context

Focus:

• memorable songs
• musical trends
• production styles
• artist stories

---

### Martin Hale — Film Editor

Primary Role:
Discuss major films and moviegoing culture.

Primary Sources:

• major film releases
• box office hits
• notable performances
• cultural response to films

Focus:

• theater experiences
• audience reactions
• memorable scenes
• why certain films connected with audiences

---

### Linda Park — Television Editor

Primary Role:
Capture the shared television experience.

Primary Sources:

• popular television programs
• network schedules
• cultural discussion surrounding TV shows

Focus:

• characters viewers loved
• famous episodes
• television trends

---

### Eve Binet — Culture & Lifestyle Editor

Primary Role:
Describe the everyday cultural experience of the year.

Primary Sources:

• fashion trends
• toys and gadgets
• malls and shopping culture
• food and restaurants
• nightlife and social habits

Focus:

• cultural fads
• lifestyle trends
• everyday experiences people shared

---

## Issue Generation Process

RetroVerse issues are generated using a structured editorial workflow.

Each issue represents one specific year of culture.

The system generates articles by assigning each RetroVerse editor a
specific topic related to that year.

---

### Step 1 — Select Year

The system begins with a target year.

Example:

1978

This year becomes the cultural focus for the issue.

---

### Step 2 — Gather Data

Relevant cultural datasets for that year are loaded.

These may include:

• Billboard Hot 100 chart data
• film releases
• television programs
• cultural trends
• notable historical events

This information becomes the research foundation used by the editors.

---

### Step 3 — Assign Editorial Topics

Each RetroVerse editor receives a topic based on their specialty.

Editor-in-Chief
Introduces the cultural tone of the year.

Nicole Thomas — Charts Editor
Analyzes the year’s chart performance.

Bob Jones — Music Features Editor
Explores memorable songs and artists.

Martin Hale — Film Editor
Discusses major films and the moviegoing experience.

Linda Park — Television Editor
Reflects on television shows that defined the year.

Eve Binet — Culture & Lifestyle Editor
Describes everyday life and cultural trends.

---

### Step 4 — Generate Articles

Each editor writes an article using their assigned voice and approved
data sources.

Articles should reflect:

• the tone of the year
• notable cultural moments
• the shared experiences of audiences

---

### Step 5 — Assemble Issue

The final RetroVerse issue includes:

• Editor-in-Chief introduction
• music chart analysis
• music feature story
• film article
• television article
• culture and lifestyle article

Together these pieces recreate the experience of living in that year.

---

### Step 6 — Publish Issue

The completed articles are assembled into the RetroVerse issue layout.

Illustrations, charts, and design elements may be added to enhance
the presentation.

The result is a magazine-style cultural snapshot of the year.

---

## RetroVerse Cover System

Purpose:
The cover introduces the cultural year featured in the issue and
establishes the visual theme for the entire magazine.

Each RetroVerse issue features one illustrated cover.

---

Cover Layout

Top Masthead

RetroVerse
Press ▶ Play for the Past

The masthead style should remain consistent across all issues
to establish brand identity.

---

Primary Cover Element

Large central illustration representing the featured year.

Examples of themes:

disco dance floor
arcade cabinets
record store interior
radio studio
movie theater marquee
mall culture

The illustration style should match the RetroVerse art direction:

1970s editorial illustration
MAD Magazine influence
comic line art with watercolor textures
slightly exaggerated cartoon proportions

---

Year Marker

Large typography displaying the issue year.

Example:

1978

The year should be visually prominent and integrated with the cover art.

---

Cover Teasers

Include 4–6 teaser headlines referencing stories inside the issue.

Example teaser categories:

Top Songs of the Year
Movies That Defined the Summer
Television Everyone Watched
Inside the Arcade Boom
Fashion of the Era
Pop Culture Flashbacks

Teasers should appear in small editorial headline boxes around the cover.

---

Footer

Small footer text:

RetroVerse Issue

Optional:

Volume number and issue date.

---

Design Rules

The cover should always feel like a vintage magazine cover
rather than a modern minimalist poster.

Avoid modern flat vector aesthetics.

Illustration should appear hand-drawn and slightly imperfect.

The color palette should reflect the cultural style of the featured year.

---

## Page 2 — RetroVerse Masthead

Purpose:
Establish the editorial identity of the magazine and list the RetroVerse
editorial staff.

Header:
RetroVerse • {year}

Tagline:
Press ▶ Play for the Past

Section Title:
Masthead

Editorial Staff

Editor-in-Chief
BJ Lovestreet

Charts Editor
Nicole Thomas

Music Features Editor
Bob Jones

Film Editor
Martin Hale

Television Editor
Linda Park

Culture & Lifestyle Editor
Eve Binet

Humor Editor
Nick Nitro

Art Director
Daisy Delgado

Publication Information

RetroVerse Magazine recreates the cultural experience of a specific year.

Content is generated from historical chart data, film releases,
television broadcasts, and cultural trends.

---

## Page 24 — RetroVerse Top 23

Purpose:
End each issue with a reference chart summarizing the year's biggest
songs.

This page is inspired by radio countdown shows but is unique to RetroVerse.

The chart lists the **RetroVerse Top 23 Songs of the Year**.

Layout Concept:

Header:
RetroVerse Top 23

Subheader:
The Biggest Songs of the Year

Display Format:
Rank
Song Title
Artist

Example Layout

1  Song Title — Artist
2  Song Title — Artist
3  Song Title — Artist
...
23 Song Title — Artist

Design Rules:

Use chart data derived from the Billboard Hot 100 dataset.

The ranking should be determined by yearly performance
(combined chart run or equivalent scoring).

This chart should NOT replicate the American Top 40 list exactly.

RetroVerse editorial adjustments may be used to produce the final Top 23.

---

## RETROVERSE PRODUCTION PIPELINE

RetroVerse issues must follow a structured editorial production pipeline modeled after a real magazine workflow.

All issue generation must follow the stages below in this exact order.

1. Year Context Generation
2. Editorial Assignment
3. Article Writing
4. Art Direction
5. Illustration Generation
6. Layout Composition
7. Press Check QA
8. PDF Build

Each stage must complete successfully before the next stage begins.

If any stage fails validation, the pipeline must stop and report the error.

### Illustration Production Rules

Illustrations must contain scene artwork only.

Illustrations must NOT contain:

• article paragraphs
• magazine headlines
• page titles
• pull quotes
• sidebars
• chart tables
• magazine layout elements

Illustrations should depict a visual moment or environment related to the article.

Examples of valid illustrations:

• movie theater crowd scene
• disco dance floor
• record store interior
• mall arcade
• living room watching television

Examples of invalid illustrations:

• magazine page layouts
• posters containing article paragraphs
• AI-generated pages containing headline text

Illustrations are background artwork used by the layout system.

All typography must be applied later by the layout engine.

### Layout System Responsibilities

The layout engine is responsible for placing all typography and layout elements.

This includes:

• article headline
• subtitle or deck
• body text
• pull quotes
• sidebars
• charts and tables
• page headers
• page numbering

The layout system must never modify the illustration artwork itself.

Illustrations must be treated as background assets.

### RetroVerse Production Rule #1

Illustrators generate artwork, not magazine pages.

## QUALITY ASSURANCE SYSTEM

RetroVerse issues must pass multiple QA checkpoints before publication.

Each checkpoint verifies a specific stage of the editorial pipeline.

### QA Stage 1 — Context Validation

Verify that the year context exists and contains required datasets.

Checks:

✔ issues/context/{year}_context.json exists
✔ Billboard datasets available
✔ RetroVerse master dataset available
✔ context file contains chart data
✔ context file contains cultural data

Fail conditions:

Missing context file
Missing chart data
Missing dataset references

### QA Stage 2 — Article Validation

Verify editorial rules are followed.

Checks:

✔ article assigned to correct RetroVerse editor voice
✔ article references data from the context file
✔ article follows the Time Perspective Rule
✔ article does not contain future knowledge phrases

Disallowed phrases include:

would later become
in hindsight
decades later
looking back today
would go on to

### QA Stage 3 — Illustration Validation

Verify illustration assets are valid editorial artwork.

Checks:

✔ illustration file exists
✔ resolution at least 2000px width
✔ illustration contains no article paragraphs
✔ illustration contains no headline typography
✔ illustration subject matches the article topic
✔ RetroVerse Easter egg frequency approximately every 3–5 illustrations

Fail conditions:

image contains paragraphs
image contains magazine layout elements
image contains article headlines

### QA Stage 4 — Layout Validation

Verify the magazine layout follows the defined issue structure.

Checks:

✔ page count between 28 and 32
✔ ISSUE_STRUCTURE order respected
✔ interior page headers formatted as "RetroVerse • {year}"
✔ masthead formatted exactly as

RetroVerse
Press ▶ Play for the Past

✔ final page is chart_top23

### QA Stage 5 — Press Check

Simulate a final print proof.

Checks:

✔ PDF file successfully generated
✔ no missing images
✔ no blank pages
✔ page numbering sequential
✔ chart pages generated from database sources

## CANONICAL DIRECTORY STRUCTURE

All RetroVerse issue generation must follow the directory structure below.

retroverse-magazine/

scripts/
Pipeline scripts and generation tools

issues/

issues/context/
Year context files

issues/{year}/

issues/{year}/articles/
Generated article text

issues/{year}/art/
Illustration assets

issues/{year}/layout/
HTML layout pages

issues/{year}/charts/
Generated chart tables

issues/{year}/pdf/
Final generated magazine

artifacts/

artifacts/logs/
Pipeline logs

artifacts/output/
Generated datasets

archive/

archive/old_runs/
Deprecated pipeline runs

archive/unused_assets/
Unused or experimental images

## ARTIFACT CLEANUP POLICY

To prevent pipeline contamination from earlier runs, the system must enforce artifact cleanup rules.

Rules:

Only files referenced by the current issue pipeline may exist inside:

issues/{year}/articles
issues/{year}/art
issues/{year}/layout

Unused files must be moved to:

archive/unused_assets/

Deprecated pipeline runs must be moved to:

archive/old_runs/

No files should be permanently deleted automatically.

Cleanup scripts should move files rather than delete them.

## RETROVERSE ILLUSTRATION STUDIO

RetroVerse illustration assignments must be made by the art direction stage before illustration prompt generation begins.

The RetroVerse illustration studio contains five canonical illustrator roles.

### COVER_ARTIST

Responsible for cover-page artwork.

Creates full-page cover scenes with strong focal storytelling, clear masthead breathing room, and bold year-defining visual energy.

### EDITORIAL_SCENE_ARTIST

Responsible for feature article illustration.

Creates page-aware editorial scenes for narrative features, cultural features, and major article pages.

Artwork must support the whole page and preserve safe zones for later layout typography.

### INFOGRAPHIC_ARTIST

Responsible for chart pages, stat pages, snapshot pages, and timeline-style information pages.

Creates restrained background structures and graphic support artwork without rendering final charts, labels, tables, or data typography into the illustration.

### COMIC_ARTIST

Responsible for comic pages and panel-based storytelling pages.

Creates sequential-storytelling artwork that supports panel rhythm, expressive action, and comic-page pacing without embedding final production lettering into the art.

### SPOT_ARTIST

Responsible for small decorative pages, utility pages, and department support art.

Creates compact editorial spot art, vignette scenes, and decorative support imagery that remains subordinate to the layout system.
