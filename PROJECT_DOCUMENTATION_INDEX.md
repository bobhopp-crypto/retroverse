# PROJECT DOCUMENTATION INDEX

Generated: 2026-03-14

Scope: all `103` Markdown files currently in the repository.

Classification rule used in this index:
- `Canonical` = intended source-of-truth for rules, schemas, paths, or behavior.
- `Supporting` = explanatory, generated, planning, QA, archived, or content-source material.

Important global finding: the documentation set is not fully self-consistent. The biggest recurring conflicts are:
- old path model vs migrated path model (`raw-data/...` and `issues/final/{year}` vs `data/raw/...` and `issues/{year}/articles/final/`)
- 1978 issue page-count drift (`14`, `30`, and `31` pages appear in different reports)
- editorial staff/name drift across `PROJECT_STATE.md`, the editorial charter, issue pages, and final story bylines
- illustration-style drift (`avoid MAD imitation` vs older `MAD-style` references)

## FILE-BY-FILE INDEX

### Repo Root and `/docs`
- `README.md` — Purpose: default Vite scaffold README for the web app root. Key sections: `React Compiler`; `Expanding the ESLint configuration`; `Configuration`. Role: Supporting. Duplicates/conflicts: not a true repository README; conflicts with the actual multi-app, multi-pipeline repository layout.
- `docs/RetroVerse Wheel Specification.md` — Purpose: defines the RetroVerse wheel feature's locked tier ranges, colors, ring layout, and animation rules. Key sections: playcount tiers; color palette; ring structure; animation behavior. Role: Canonical. Duplicates/conflicts: no direct duplicate found; narrow feature-specific source of truth.
- `docs/TRUNK_STABILIZATION_REPORT.md` — Purpose: verifies the migrated trunk layout, corrected paths, and current build health. Key sections: `Directory Verification`; `Dataset Verification`; `Scripts Checked`; `Paths Corrected`; `Pipelines Tested`; `Build Results`; `Unresolved Issues`; `Repository Stability`. Role: Supporting. Duplicates/conflicts: overlaps `docs/TRUNK_STABILIZATION_PLAN.md` and `docs/MIGRATION_EXECUTION_REPORT.md`; it is the current validation report, not the original design spec.
- `docs/REGISTRY_PIPELINE_INTEGRATION.md` — Purpose: implementation record for wiring pipelines to `data/registry/DATA_REGISTRY.yaml`. Key sections: `Summary`; `Added Helpers`; `Registry Entries Added`; `Updated Files`; `Path Resolution Changes`; `Fallback Behavior`; `Verification`; `Notes`. Role: Supporting. Duplicates/conflicts: complements `docs/DATA_REGISTRY.md`; not itself canonical policy.
- `docs/DSM_WEBSTACK_RECOVERY.md` — Purpose: operational recovery runbook for a Synology DSM web stack. Key sections: prerequisites; identify; stop services; kill port holders; remove stale files; validate nginx; restart; test; inspect logs. Role: Supporting. Duplicates/conflicts: no obvious duplicate in Markdown; operationally unrelated to the RetroVerse content pipeline.
- `docs/DATA_REGISTRY.md` — Purpose: defines the repository's dataset registry schema, ownership model, directory layout, and consumption rules. Key sections: `Purpose`; `Dataset Schema`; `Data Directory Layout`; `Adding New Datasets`; `How Pipelines Should Reference Datasets`; `How Apps Should Consume Derived Data`; `Cultural Datasets`. Role: Canonical. Duplicates/conflicts: largely supersedes older inventory docs such as `docs/DATA_INVENTORY.md`; should be preferred for current data-path governance.
- `docs/DATA_LINEAGE.md` — Purpose: generated lineage snapshot of registered datasets, producers, and consumers. Key sections: `Summary`; `Raw Datasets`; `Derived Datasets`; `Producer And Consumer Map`; `Automatic Lineage Generation`; `Graph Rendering`. Role: Supporting. Duplicates/conflicts: depends on `docs/DATA_REGISTRY.md` and the registry YAML; generated reference, not rule-defining documentation.
- `docs/LINEAGE_AUTOMATION_REPORT.md` — Purpose: implementation report for automated lineage regeneration hooks and graph rendering. Key sections: `Clustering Changes`; `Pipeline Hooks Added`; `Graphviz Detection Behavior`; `Verification Results`. Role: Supporting. Duplicates/conflicts: overlaps `docs/DATA_LINEAGE.md` and `docs/DATA_REGISTRY_IMPLEMENTATION.md`; historical implementation detail rather than source-of-truth.
- `docs/REPOSITORY_ARCHITECTURE_AUDIT.md` — Purpose: broad repository audit covering active systems, redundant components, data-source conflicts, and migration recommendations. Key sections: `PROJECT STRUCTURE`; `PIPELINE INVENTORY`; `DATA SOURCES`; `REDUNDANT COMPONENTS`; `UNUSED SCRIPTS`; `LIKELY FAILURE POINTS`; `ARCHITECTURE RECOMMENDATION`. Role: Supporting. Duplicates/conflicts: overlaps `docs/TRUNK_STABILIZATION_PLAN.md`, `docs/MIGRATION_EXECUTION_REPORT.md`, and magazine-specific audits; some issues were later stabilized.
- `docs/DATA_REGISTRY_IMPLEMENTATION.md` — Purpose: change log for creating the registry, registering datasets, and validating coverage. Key sections: `Summary`; `Datasets Registered`; `Pipelines Linked`; `Validation Results`; `Files Created`; `Registry Completion`; `Recommendations for Future Datasets`. Role: Supporting. Duplicates/conflicts: superseded by the living registry docs and current validation status; useful as historical record only.
- `docs/MIGRATION_VERIFICATION.md` — Purpose: pre-execution verification and migration planning checklist for repository restructuring. Key sections: canonical dataset verification; migration script review; commit plan; exact `git mv` operations; scripts that will break; final checklist. Role: Supporting. Duplicates/conflicts: planning-stage document superseded by `docs/MIGRATION_EXECUTION_REPORT.md` and `docs/TRUNK_STABILIZATION_REPORT.md`.
- `docs/DATA_INVENTORY.md` — Purpose: pre-registry inventory of raw data, derived data, and pipeline scripts. Key sections: `DATA SOURCES`; `DATABASE FILES`; `CSV FILES`; `JSON FILES`; `PIPELINE SCRIPTS`; `BILLBOARD DATA CAPABILITY CHECK`; `READ-ONLY RULE CONFIRMATION`. Role: Supporting. Duplicates/conflicts: overlaps `docs/DATA_REGISTRY.md`; uses older path conventions and is partially stale after migration.
- `docs/MIGRATION_EXECUTION_REPORT.md` — Purpose: execution log for the repo move into `/apps`, `/pipelines`, `/data`, and `/archive`. Key sections: `Summary`; `Files Moved`; `Paths Updated`; `Scripts Checked`; `Issues Detected`; `Final Layout`. Role: Supporting. Duplicates/conflicts: supersedes `docs/REPOSITORY_MIGRATION_SCRIPT.md` and much of `docs/MIGRATION_VERIFICATION.md`; historical execution record, not an ongoing spec.
- `docs/REPOSITORY_MIGRATION_SCRIPT.md` — Purpose: simulated migration playbook for the restructuring effort. Key sections: `Scope`; `Assumptions`; `Exact Move Map`; `Proposed Migration Script`; `Canonical Billboard Dataset Handling`; `Scripts And Configs That Need Path Updates`; `Recommended Execution Order`. Role: Supporting. Duplicates/conflicts: explicitly a planning simulation; superseded by `docs/MIGRATION_EXECUTION_REPORT.md`.
- `docs/UNREGISTERED_DATASETS.md` — Purpose: report of datasets missing from the registry at generation time. Key sections: `Summary`; `Suggested Entries`; `Suggested YAML Entries`. Role: Supporting. Duplicates/conflicts: directly contradicted by later registry-completion docs showing no remaining unregistered datasets; outdated.
- `docs/TRUNK_STABILIZATION_PLAN.md` — Purpose: design document for deciding which systems belong in the supported trunk and how to restructure the repo. Key sections: active trunk systems; legacy experiments; proposed top-level structure; canonical Billboard dataset; dependent pipelines; migration plan; final recommended trunk shape; execution order. Role: Supporting. Duplicates/conflicts: superseded by `docs/MIGRATION_EXECUTION_REPORT.md` and `docs/TRUNK_STABILIZATION_REPORT.md`.

### Magazine Governance, Architecture, and Process Docs
- `apps/magazine/retroverse-magazine/ISSUE_STRUCTURE_REPORT.md` — Purpose: verification report for the 1978 issue's canonical page order and template coverage. Key sections: `Summary`; `Confirmed Page Order`; `Final Page Count`; `Missing Templates`; `Pipeline Integration Status`; `Verification Notes`. Role: Supporting. Duplicates/conflicts: conflicts with `PIPELINE_REPAIR_REPORT.md` and `PRESS_CHECK_1978.md` on total page count and layout state.
- `apps/magazine/retroverse-magazine/layout-library/docs/retroverse_layout_library.md` — Purpose: defines layout philosophy, archetypes, template-selection rules, and page-composition behavior. Key sections: `RetroVerse Page Philosophy`; `Why Page Templates Matter`; `How the Issue Generator Should Choose Templates`; `How Illustrations, Artifacts, Sidebars, and Text Blocks Interact`; `Staying Varied While Remaining Consistent`; `RetroVerse Page Archetypes`; `How the Issue Builder Should Use This Library`. Role: Canonical. Duplicates/conflicts: partially conflicts with later anti-MAD guidance because it still references `MAD-style rhythm shifts`.
- `apps/magazine/retroverse-magazine/layout-library/docs/page_rhythm_guide.md` — Purpose: defines pacing/rhythm rules for issue sequencing. Key sections: `Core Principle`; `Practical Rhythm Rules`; `Recommended Visual Density Tags`; `Example Sequence: 24-Page Issue`; `Example Sequence: 48-Page Issue`; `Sequence Checklist for Editors and Builders`. Role: Canonical. Duplicates/conflicts: no direct duplicate; examples assume 24/48-page structures while 1978 reports discuss 30/31-page builds.
- `apps/magazine/retroverse-magazine/PRESS_CHECK_1978.md` — Purpose: pre-repair press check report for the 1978 issue. Key sections: `Pipeline Status`; `Page Count`; `Masthead Verification`; `Image Rendering Verification`; `Page Structure Verification`; `Chart Page Verification`; `Easter Egg Rule Verification`; `PDF Output Verification`; `Layout Issues Found`; `Recommended Fixes`. Role: Supporting. Duplicates/conflicts: directly conflicts with later pass-state docs such as `ISSUE_STRUCTURE_REPORT.md` and `artifacts/output/1978/qa/1978_press_check_QA.md`; likely outdated.
- `apps/magazine/retroverse-magazine/PROJECT_AUDIT.md` — Purpose: broad audit of the magazine project's fragmented pre-repair state. Key sections: `Executive Summary`; `PROJECT STRUCTURE MAP`; `PIPELINE STATUS`; `ILLUSTRATION SYSTEM STATUS`; `ISSUE 1978 ANALYSIS`; `MAGAZINE BUILDER STATUS`; `REDUNDANT SYSTEMS`; `MISSING COMPONENTS`; `RECOMMENDED NEXT ACTION`. Role: Supporting. Duplicates/conflicts: overlaps `MAGAZINE_PIPELINE_AUDIT.md`, `PROJECT_PIPELINE_REPORT.md`, and later repair docs; much of it reflects an earlier state.
- `apps/magazine/retroverse-magazine/PIPELINE_REPAIR_REPORT.md` — Purpose: summary of fixes applied to repair the magazine pipeline and produce a working issue/PDF. Key sections: `Issues Found`; `Files Modified`; `Fixes Applied`; `Final Page Count`; `Verification Results`; `Notes`. Role: Supporting. Duplicates/conflicts: conflicts with `ISSUE_STRUCTURE_REPORT.md` on `31` vs `30` pages and chart-page placement; overlaps `PIPELINE_REPAIR_IMPLEMENTATION.md`.
- `apps/magazine/retroverse-magazine/PIPELINE_REPAIR_IMPLEMENTATION.md` — Purpose: implementation record of moved files, new stage structure, new QA gates, and canonical output paths. Key sections: `Files moved`; `Scripts modified`; `New pipeline structure`; `Directories created`; `Illustration rule enforcement`; `Canonical output paths`; `Verification run`. Role: Supporting. Duplicates/conflicts: overlaps `CANONICAL_PIPELINE.md`, but is more accurate about current `issues/{year}/articles/final/` and `issues/{year}/layout/` paths.
- `apps/magazine/retroverse-magazine/charter/retroverse_editorial_charter.md` — Purpose: defines magazine voice, persona profiles, and tone rules for contributors. Key sections: editor-in-chief; music editor; film & television critics; culture columnist; charts narrator; advice column; art director; editorial tone rules. Role: Canonical. Duplicates/conflicts: conflicts with `PROJECT_STATE.md` and live issue files on staff names (`Emily Bennett/Charles Carter/Hanna Judge` vs `Emily Bennet/Charles Cursor/Daisy Delgado`, plus Bob Jones/Martin Hale/Linda Park/Eve Binet in issue pages).
- `apps/magazine/retroverse-magazine/MAGAZINE_PIPELINE_AUDIT.md` — Purpose: full compliance audit of the magazine repo against `PROJECT_STATE.md`. Key sections: `Repository Overview`; `Directory Tree`; `Pipeline Script Inventory`; `Pipeline Stage Coverage`; `Directory Structure Compliance`; `Artwork Violations`; `Unused Files`; `Recommended Cleanup Plan`; `Conformance Summary`. Role: Supporting. Duplicates/conflicts: overlaps `PROJECT_AUDIT.md` and `PROJECT_PIPELINE_REPORT.md`; partially outdated because some directories/paths it marked missing were later created.
- `apps/magazine/retroverse-magazine/PROJECT_STATE.md` — Purpose: foundational magazine specification covering data sources, editorial rules, brand rules, issue structure, production pipeline, QA, directories, and illustration policy. Key sections: `Purpose`; `Data Sources`; `Year Context System`; `Screen & Culture Warehouse`; `Editorial Staff`; `RetroVerse Brand System`; `RetroVerse Issue Structure`; `Generation Rules`; `Charts System`; `Editorial Voice Profiles`; `Issue Generation Process`; `RETROVERSE PRODUCTION PIPELINE`; `QUALITY ASSURANCE SYSTEM`; `CANONICAL DIRECTORY STRUCTURE`; `RETROVERSE ILLUSTRATION STUDIO`. Role: Canonical. Duplicates/conflicts: internally inconsistent on staff roster and style references, and partially stale on paths relative to current migrated repo structure.
- `apps/magazine/retroverse-magazine/prompts/generate_issue_prompt.md` — Purpose: intended prompt file for issue generation. Key sections: none; file is empty. Role: Supporting. Duplicates/conflicts: empty stub; provides no usable guidance and effectively documents a missing prompt spec.
- `apps/magazine/retroverse-magazine/templates/issue_template.md` — Purpose: intended issue template Markdown. Key sections: none; file is empty. Role: Supporting. Duplicates/conflicts: empty stub; does not currently serve as usable documentation or template source.
- `apps/magazine/retroverse-magazine/docs/CANONICAL_PIPELINE.md` — Purpose: declares the intended canonical magazine pipeline stages and inputs. Key sections: pipeline stages from context through issue build; `Canonical Inputs`; `Archived Prototype Systems`. Role: Canonical. Duplicates/conflicts: stale on current file paths (`issues/final/{year}` and `issues/layout/{year}_production_targets.json`) compared with `PIPELINE_REPAIR_IMPLEMENTATION.md` and the current repo tree.
- `apps/magazine/retroverse-magazine/docs/SCREEN_CULTURE_WAREHOUSE_AUDIT.md` — Purpose: generated coverage audit for the screen-culture warehouse across years. Key sections: `Coverage Summary`; `Per-Year Coverage`; weak years; field sparsity; recommendations. Role: Supporting. Duplicates/conflicts: no direct duplicate; point-in-time quality report.
- `apps/magazine/retroverse-magazine/docs/SCREEN_CULTURE_DATA_AUDIT.md` — Purpose: generated audit of screen-culture data completeness and gaps for magazine use. Key sections: `Thresholds`; `Source Detection`; `Per-Year Counts`; `Coverage Warnings`; `Dataset Gaps`. Role: Supporting. Duplicates/conflicts: complements the warehouse audit; report state may age as data refreshes.
- `apps/magazine/retroverse-magazine/docs/PROJECT_PIPELINE_REPORT.md` — Purpose: current script and directory inventory for the magazine pipeline, with illustration-flow and failure-point analysis. Key sections: `PROJECT DIRECTORY TREE`; `SCRIPT INVENTORY`; `ILLUSTRATION PIPELINE FLOW`; `PROMPT MAPPING`; `CACHE LOGIC`; `POSSIBLE FAILURE POINTS`; `SAMPLE EXECUTION TRACE`. Role: Supporting. Duplicates/conflicts: overlaps `MAGAZINE_PIPELINE_AUDIT.md`; more implementation-oriented than policy-oriented.
- `apps/magazine/retroverse-magazine/docs/ARCHITECTURE.md` — Purpose: high-level magazine architecture and layer model. Key sections: `Data Layer`; `Editorial Layer`; `Art Layer`; `Layout Layer`; `Supervisor Layer`; `Data Flow`; `Music Data Layers`; `Screen & Culture Warehouse`. Role: Canonical. Duplicates/conflicts: broadly consistent with the project spec, but it does not resolve the path and staff-name conflicts found elsewhere.
- `apps/magazine/retroverse-magazine/DATA_INVENTORY.md` — Purpose: magazine-specific inventory of canonical data sources, data files, scripts, generated issues, art library, and prompt assets. Key sections: `Project Structure`; `Canonical Data Sources`; `Data Files`; `Databases`; `Scripts`; `Generated Issues`; `Artwork Library`; `Prompt Templates`; `Observations`. Role: Supporting. Duplicates/conflicts: overlaps repo-level `docs/DATA_INVENTORY.md` and `docs/DATA_REGISTRY.md`; many references still point at older path conventions.

### Magazine Workflow and QA Docs
- `apps/magazine/retroverse-magazine/workflow/page_rebuild/README.md` — Purpose: documents the controlled single-page rebuild workflow for one page at a time. Key sections: workflow scope; goals; main scripts; output location; relation to canonical issue outputs. Role: Supporting. Duplicates/conflicts: prototype workflow that overlaps issue-wide pipeline stages but is explicitly non-canonical.
- `apps/magazine/retroverse-magazine/workflow/page_rebuild/SINGLE_PAGE_REBUILD_REPORT.md` — Purpose: reports what the single-page rebuild workflow created and verified. Key sections: `Scope`; `Files Created`; `QA Results`; `Readiness`; `Recommended Next Step`. Role: Supporting. Duplicates/conflicts: overlaps issue-wide QA artifacts in `artifacts/output/1978/qa/`; limited to the `movies` page.
- `apps/magazine/retroverse-magazine/workflow/page_rebuild/output/1978_movies_page_brief_QA.md` — Purpose: QA gate output for the rebuilt `movies` page brief. Key sections: `Checks`; `Notes`. Role: Supporting. Duplicates/conflicts: overlaps issue-wide `1978_page_briefs_QA.md`, but only for one page.
- `apps/magazine/retroverse-magazine/workflow/page_rebuild/output/1978_movies_art_direction_QA.md` — Purpose: QA gate output for the rebuilt `movies` page art direction. Key sections: `Checks`; `Notes`. Role: Supporting. Duplicates/conflicts: overlaps issue-wide `1978_art_direction_QA.md`, but only for one page.
- `apps/magazine/retroverse-magazine/workflow/page_rebuild/output/1978_movies_art_prompt_QA.md` — Purpose: QA gate output for the rebuilt `movies` page art prompt. Key sections: `Checks`; `Notes`. Role: Supporting. Duplicates/conflicts: overlaps issue-wide `1978_art_prompt_QA.md`, but only for one page.
- `apps/magazine/retroverse-magazine/workflow/page_rebuild/output/1978_movies_layout_QA.md` — Purpose: QA gate output for the rebuilt `movies` page layout. Key sections: `Checks`; `Notes`. Role: Supporting. Duplicates/conflicts: overlaps issue-wide `1978_layout_QA.md`, but only for one page.
- `apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_page_briefs_QA.md` — Purpose: generated issue-wide QA report for page briefs. Key sections: `Checks`; `Notes`. Role: Supporting. Duplicates/conflicts: later-stage artifact that broadly supersedes the single-page brief QA in workflow output.
- `apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_art_direction_QA.md` — Purpose: generated issue-wide QA report for art direction. Key sections: `Checks`; `Notes`. Role: Supporting. Duplicates/conflicts: later-stage artifact that broadly supersedes the single-page art-direction QA in workflow output.
- `apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_art_prompt_QA.md` — Purpose: generated issue-wide QA report for art prompts. Key sections: `Checks`; `Notes`. Role: Supporting. Duplicates/conflicts: later-stage artifact that broadly supersedes the single-page art-prompt QA in workflow output.
- `apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_layout_QA.md` — Purpose: generated issue-wide QA report for layout. Key sections: `Checks`; `Notes`. Role: Supporting. Duplicates/conflicts: later-stage artifact that broadly supersedes the single-page layout QA in workflow output.
- `apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_press_check_QA.md` — Purpose: generated issue-wide press-check QA report. Key sections: `Checks`; `Notes`. Role: Supporting. Duplicates/conflicts: functionally replaces the failing narrative in `PRESS_CHECK_1978.md` with a pass-state artifact.

### 1978 Planning, Layout, and Section Source Docs
- `apps/magazine/retroverse-magazine/issues/plans/1978_narrative_plan.md` — Purpose: editorial plan for the 1978 issue's identity, table of contents, story assignments, and visual concepts. Key sections: `Year Identity`; `Proposed Table Of Contents`; `Story Assignments`; `Chart Highlights`; `Year Snapshot Boxes`; `Visual Concepts`. Role: Supporting. Duplicates/conflicts: upstream planning artifact that feeds stories and layout; partially overlaps `retroverse_1978_pilot.md`.
- `apps/magazine/retroverse-magazine/issues/1978/layout/1978_issue_map.md` — Purpose: layout and design assignment map for the 1978 issue. Key sections: `Issue Map`; `Story Design Assignments`; `Visual Briefs`; `Anchor Reuse Warnings`. Role: Supporting. Duplicates/conflicts: paired with non-Markdown production-target JSON; old docs still reference its former `issues/layout/` location.
- `apps/magazine/retroverse-magazine/issues/1978/cover.md` — Purpose: cover-page copy and teaser package for the 1978 issue. Key sections: `Press ▶ Play for the Past`; `Cover Teasers`; `Cover Illustration Description`; `Footer`. Role: Supporting. Duplicates/conflicts: no direct duplicate; serves as page-source content rather than documentation.
- `apps/magazine/retroverse-magazine/issues/1978/masthead.md` — Purpose: masthead page content and publication information for the 1978 issue. Key sections: `Press ▶ Play for the Past`; `Masthead`; `Editorial Staff`; `Publication Information`. Role: Supporting. Duplicates/conflicts: staff roster conflicts with `PROJECT_STATE.md` and the charter by using `Bob Jones`, `Martin Hale`, `Linda Park`, and `Eve Binet`.
- `apps/magazine/retroverse-magazine/issues/1978/editor_letter.md` — Purpose: editor's opening letter for the 1978 issue. Key sections: `Editor Letter`. Role: Supporting. Duplicates/conflicts: thematically overlaps the combined editorial in `retroverse_1978_pilot.md`; no direct structural conflict.
- `apps/magazine/retroverse-magazine/issues/1978/charts_overview.md` — Purpose: charts-analysis department page for 1978. Key sections: `Chart Lens`; `Lyric Lens`; `Performance Signals From the Context File`; `What This Means for the Issue`. Role: Supporting. Duplicates/conflicts: complements `chart_top23.md` and story files; no direct duplicate.
- `apps/magazine/retroverse-magazine/issues/1978/movies.md` — Purpose: movies department page for 1978. Key sections: `Context Notes`. Role: Supporting. Duplicates/conflicts: byline uses `Martin Hale`, which conflicts with the top-level staff block and charter naming.
- `apps/magazine/retroverse-magazine/issues/1978/television.md` — Purpose: television department page for 1978. Key sections: `Context Notes`. Role: Supporting. Duplicates/conflicts: byline uses `Linda Park`, which conflicts with the top-level staff block and charter naming.
- `apps/magazine/retroverse-magazine/issues/1978/culture.md` — Purpose: culture/lifestyle department page for 1978. Key sections: `Context Notes`. Role: Supporting. Duplicates/conflicts: byline uses `Eve Binet`, which conflicts with the top-level staff block and charter naming.
- `apps/magazine/retroverse-magazine/issues/1978/letters.md` — Purpose: letters page for the 1978 issue. Key sections: reader letters only. Role: Supporting. Duplicates/conflicts: no direct duplicate found.
- `apps/magazine/retroverse-magazine/issues/1978/chart_top23.md` — Purpose: Top 23 chart page for the 1978 issue. Key sections: `The Biggest Songs of the Year`. Role: Supporting. Duplicates/conflicts: placement conflicts across docs: `PROJECT_STATE.md` describes `Page 24`, while later structure reports place it at the end of a `30` or `31` page issue.
- `apps/magazine/retroverse-magazine/issues/1978/arcade.md` — Purpose: intended arcade/technology page source. Key sections: title only. Role: Supporting. Duplicates/conflicts: placeholder-only file; effectively incomplete and overlaps generated placeholder handling described in `ISSUE_STRUCTURE_REPORT.md`.
- `apps/magazine/retroverse-magazine/issues/1978/ads.md` — Purpose: intended retro-ad page source. Key sections: title only. Role: Supporting. Duplicates/conflicts: placeholder-only file; concept overlaps `retro_ad` and `retro_ads_page` names seen in issue-structure docs.
- `apps/magazine/retroverse-magazine/issues/1978/comic.md` — Purpose: intended comic page source. Key sections: title only. Role: Supporting. Duplicates/conflicts: placeholder-only file; current content is incomplete.
- `apps/magazine/retroverse-magazine/issues/1978/puzzle1.md` — Purpose: intended first puzzle page source. Key sections: title only. Role: Supporting. Duplicates/conflicts: placeholder-only file; highly redundant with `puzzle2.md`.
- `apps/magazine/retroverse-magazine/issues/1978/puzzle2.md` — Purpose: intended second puzzle page source. Key sections: title only. Role: Supporting. Duplicates/conflicts: placeholder-only file; highly redundant with `puzzle1.md`.
- `apps/magazine/retroverse-magazine/issues/1978/retroverse_1978_pilot.md` — Purpose: old monolithic pilot-issue draft combining editorial, feature, film/TV, culture, advice, chart watch, and closing into one file. Key sections: editorial; feature story; film & television; culture & trends; advice column; chart watch; end page. Role: Supporting. Duplicates/conflicts: superseded by the modular issue-page package in `issues/1978/` and the story/article system.

### 1978 Song Source Docs
- `apps/magazine/retroverse-magazine/issues/1978/songs/01.md` — Purpose: top-song page for `Stayin' Alive — Bee Gees`. Key sections: `Data Snapshot`. Role: Supporting. Duplicates/conflicts: part of the 10-song package; byline uses `Bob Jones`, which matches older voice-profile sections but conflicts with the top-level staff block and charter.
- `apps/magazine/retroverse-magazine/issues/1978/songs/02.md` — Purpose: top-song page for `Night Fever — Bee Gees`. Key sections: `Data Snapshot`. Role: Supporting. Duplicates/conflicts: same byline/staff conflict as the other song files.
- `apps/magazine/retroverse-magazine/issues/1978/songs/03.md` — Purpose: top-song page for `(Love Is) Thicker Than Water — Andy Gibb`. Key sections: `Data Snapshot`. Role: Supporting. Duplicates/conflicts: same byline/staff conflict as the other song files.
- `apps/magazine/retroverse-magazine/issues/1978/songs/04.md` — Purpose: top-song page for `Three Times A Lady — Commodores`. Key sections: `Data Snapshot`. Role: Supporting. Duplicates/conflicts: same byline/staff conflict as the other song files.
- `apps/magazine/retroverse-magazine/issues/1978/songs/05.md` — Purpose: top-song page for `Kiss You All Over — Exile`. Key sections: `Data Snapshot`. Role: Supporting. Duplicates/conflicts: same byline/staff conflict as the other song files.
- `apps/magazine/retroverse-magazine/issues/1978/songs/06.md` — Purpose: top-song page for `Can't Smile Without You — Barry Manilow`. Key sections: `Data Snapshot`. Role: Supporting. Duplicates/conflicts: same byline/staff conflict as the other song files.
- `apps/magazine/retroverse-magazine/issues/1978/songs/07.md` — Purpose: top-song page for `MacArthur Park — Donna Summer`. Key sections: `Data Snapshot`. Role: Supporting. Duplicates/conflicts: same byline/staff conflict as the other song files.
- `apps/magazine/retroverse-magazine/issues/1978/songs/08.md` — Purpose: top-song page for `Lay Down Sally — Eric Clapton`. Key sections: `Data Snapshot`. Role: Supporting. Duplicates/conflicts: same byline/staff conflict as the other song files.
- `apps/magazine/retroverse-magazine/issues/1978/songs/09.md` — Purpose: top-song page for `Shadow Dancing — Andy Gibb`. Key sections: `Data Snapshot`. Role: Supporting. Duplicates/conflicts: same byline/staff conflict as the other song files.
- `apps/magazine/retroverse-magazine/issues/1978/songs/10.md` — Purpose: top-song page for `Boogie Oogie Oogie — A Taste Of Honey`. Key sections: `Data Snapshot`. Role: Supporting. Duplicates/conflicts: same byline/staff conflict as the other song files.

### 1978 Story Draft Docs
- `apps/magazine/retroverse-magazine/issues/1978/articles/story_001.md` — Purpose: draft story on soundtrack crossover culture in 1978. Key sections: `Lede`; `Analysis`; `Data Highlights`; `Cultural Context`; `Closing`; `Sources Used`. Role: Supporting. Duplicates/conflicts: draft counterpart to `issues/1978/articles/final/story_001.md`; final version should win for build use.
- `apps/magazine/retroverse-magazine/issues/1978/articles/story_002.md` — Purpose: draft story on the Bee Gees power curve. Key sections: `Lede`; `Analysis`; `Data Highlights`; `Cultural Context`; `Closing`; `Sources Used`. Role: Supporting. Duplicates/conflicts: draft counterpart to `issues/1978/articles/final/story_002.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/story_003.md` — Purpose: draft story on `Stayin' Alive` moving from debut to Top 10. Key sections: `Lede`; `Analysis`; `Data Highlights`; `Cultural Context`; `Closing`; `Sources Used`. Role: Supporting. Duplicates/conflicts: draft counterpart to `issues/1978/articles/final/story_003.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/story_004.md` — Purpose: draft story on the fastest climb of the year. Key sections: `Lede`; `Analysis`; `Data Highlights`; `Cultural Context`; `Closing`; `Sources Used`. Role: Supporting. Duplicates/conflicts: draft counterpart to `issues/1978/articles/final/story_004.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/story_005.md` — Purpose: draft story on the sharpest chart drop of the year. Key sections: `Lede`; `Analysis`; `Data Highlights`; `Cultural Context`; `Closing`; `Sources Used`. Role: Supporting. Duplicates/conflicts: draft counterpart to `issues/1978/articles/final/story_005.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/story_006.md` — Purpose: draft story on `Saturday Night Fever` album gravity. Key sections: `Lede`; `Analysis`; `Data Highlights`; `Cultural Context`; `Closing`; `Sources Used`. Role: Supporting. Duplicates/conflicts: draft counterpart to `issues/1978/articles/final/story_006.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/story_007.md` — Purpose: draft story on the slow climb of `Rumours`. Key sections: `Lede`; `Analysis`; `Data Highlights`; `Cultural Context`; `Closing`; `Sources Used`. Role: Supporting. Duplicates/conflicts: draft counterpart to `issues/1978/articles/final/story_007.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/story_008.md` — Purpose: draft screen-year pulse story anchored to `Grease`. Key sections: `Lede`; `Analysis`; `Data Highlights`; `Cultural Context`; `Closing`; `Sources Used`. Role: Supporting. Duplicates/conflicts: draft counterpart to `issues/1978/articles/final/story_008.md`; heading still exposes a raw dictionary literal instead of cleaned editorial text.
- `apps/magazine/retroverse-magazine/issues/1978/articles/story_009.md` — Purpose: draft TV story anchored to `Mork and Mindy`. Key sections: `Lede`; `Analysis`; `Data Highlights`; `Cultural Context`; `Closing`; `Sources Used`. Role: Supporting. Duplicates/conflicts: draft counterpart to `issues/1978/articles/final/story_009.md`; heading still exposes a raw dictionary literal instead of cleaned editorial text.
- `apps/magazine/retroverse-magazine/issues/1978/articles/story_010.md` — Purpose: draft week-by-week yearline story. Key sections: `Lede`; `Analysis`; `Data Highlights`; `Cultural Context`; `Closing`; `Sources Used`. Role: Supporting. Duplicates/conflicts: draft counterpart to `issues/1978/articles/final/story_010.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/story_011.md` — Purpose: draft story on an `almost hit` for Barry Manilow. Key sections: `Lede`; `Analysis`; `Data Highlights`; `Cultural Context`; `Closing`; `Sources Used`. Role: Supporting. Duplicates/conflicts: draft counterpart to `issues/1978/articles/final/story_011.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/story_012.md` — Purpose: draft story for the sonic fingerprint card set. Key sections: `Lede`; `Analysis`; `Data Highlights`; `Cultural Context`; `Closing`; `Sources Used`. Role: Supporting. Duplicates/conflicts: draft counterpart to `issues/1978/articles/final/story_012.md`.

### 1978 Final Story Docs
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/story_001.md` — Purpose: final article on soundtrack crossover culture in 1978. Key sections: `Lede`; `Analysis`; `Data Context`; `Cultural Significance`; `Closing`; `Data References`. Role: Supporting. Duplicates/conflicts: supersedes `issues/1978/articles/story_001.md`; current content source, but still content rather than policy documentation.
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/story_002.md` — Purpose: final article on the Bee Gees power curve. Key sections: `Lede`; `Analysis`; `Data Context`; `Cultural Significance`; `Closing`; `Data References`. Role: Supporting. Duplicates/conflicts: supersedes `issues/1978/articles/story_002.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/story_003.md` — Purpose: final article on `Stayin' Alive` reaching the Top 10. Key sections: `Lede`; `Analysis`; `Data Context`; `Cultural Significance`; `Closing`; `Data References`. Role: Supporting. Duplicates/conflicts: supersedes `issues/1978/articles/story_003.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/story_004.md` — Purpose: final article on the fastest climb of the year. Key sections: `Lede`; `Analysis`; `Data Context`; `Cultural Significance`; `Closing`; `Data References`. Role: Supporting. Duplicates/conflicts: supersedes `issues/1978/articles/story_004.md`; byline uses `Kevin Casey`, who is not in the current top-level staff block or charter.
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/story_005.md` — Purpose: final article on the sharpest chart drop of the year. Key sections: `Lede`; `Analysis`; `Data Context`; `Cultural Significance`; `Closing`; `Data References`. Role: Supporting. Duplicates/conflicts: supersedes `issues/1978/articles/story_005.md`; byline uses `Kevin Casey`, who is not in the current top-level staff block or charter.
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/story_006.md` — Purpose: final article on `Saturday Night Fever` album gravity. Key sections: `Lede`; `Analysis`; `Data Context`; `Cultural Significance`; `Closing`; `Data References`. Role: Supporting. Duplicates/conflicts: supersedes `issues/1978/articles/story_006.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/story_007.md` — Purpose: final article on the slow climb of `Rumours`. Key sections: `Lede`; `Analysis`; `Data Context`; `Cultural Significance`; `Closing`; `Data References`. Role: Supporting. Duplicates/conflicts: supersedes `issues/1978/articles/story_007.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/story_008.md` — Purpose: final screen-year pulse article anchored to `Grease`. Key sections: `Lede`; `Analysis`; `Data Context`; `Cultural Significance`; `Closing`; `Data References`. Role: Supporting. Duplicates/conflicts: supersedes `issues/1978/articles/story_008.md`; heading still exposes a raw dictionary literal and the byline `Lola Vance` does not appear in the current staff docs.
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/story_009.md` — Purpose: final TV article anchored to `Mork and Mindy`. Key sections: `Lede`; `Analysis`; `Data Context`; `Cultural Significance`; `Closing`; `Data References`. Role: Supporting. Duplicates/conflicts: supersedes `issues/1978/articles/story_009.md`; heading still exposes a raw dictionary literal and the byline `Lola Vance` does not appear in the current staff docs.
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/story_010.md` — Purpose: final week-by-week yearline article. Key sections: `Lede`; `Analysis`; `Data Context`; `Cultural Significance`; `Closing`; `Data References`. Role: Supporting. Duplicates/conflicts: supersedes `issues/1978/articles/story_010.md`; byline uses `Professor Wheeler`, which is probably the same persona as `Prof` Dick Wheeler but should be normalized.
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/story_011.md` — Purpose: final `almost hit` article for Barry Manilow. Key sections: `Lede`; `Analysis`; `Data Context`; `Cultural Significance`; `Closing`; `Data References`. Role: Supporting. Duplicates/conflicts: supersedes `issues/1978/articles/story_011.md`.
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/story_012.md` — Purpose: final sonic fingerprint card-set article. Key sections: `Lede`; `Analysis`; `Data Context`; `Cultural Significance`; `Closing`; `Data References`. Role: Supporting. Duplicates/conflicts: supersedes `issues/1978/articles/story_012.md`.

### Active Pipeline, Archive, and Derived Data Markdown
- `pipelines/support-data/README.md` — Purpose: README for generating the cross-year cultural support CSV. Key sections: `Setup`; `Run`; `Common Commands`. Role: Supporting. Duplicates/conflicts: path examples still point to the older `retroverse-output/` location instead of the migrated `pipelines/support-data/` and registry-led structure.
- `archive/pipelines/retroverse-1974/README.md` — Purpose: archived README for the older illustrated 1974 artifact engine. Key sections: `Run`; `Rendering Credentials`; `One-Command Batch`. Role: Supporting. Duplicates/conflicts: archived overlap with the active `pipelines/cards-1974` flow and the 1974 derived markdown files.
- `archive/pipelines/tools-legacy/README.md` — Purpose: archived README for the TypeScript tools-pipeline scaffold. Key sections: `Project layout`; `Pipeline stages (intended flow)`; `Module interactions`; `Configuration`; `How to run`; `Next steps`. Role: Supporting. Duplicates/conflicts: explicitly duplicates the active media-pipeline concept while remaining unfinished.
- `archive/pipelines/tools-legacy/media-normalization/README.md` — Purpose: archived note for a folder-action MP4 normalization utility. Key sections: single operation description only. Role: Supporting. Duplicates/conflicts: no obvious duplicate in Markdown; archived utility doc.
- `archive/docs/Journal/rv_journal.md` — Purpose: historical project journal mixing creative and technical milestones. Key sections: dated journal entries from late 2025 onward. Role: Supporting. Duplicates/conflicts: no direct duplicate; archival narrative rather than system documentation.
- `data/derived/cards/1974/1974_weekly_context.md` — Purpose: generated weekly 1974 chart/context table used by the 1974 cards system. Key sections: no headings; tabular weekly context data. Role: Supporting. Duplicates/conflicts: generated data artifact that overlaps the JSON context and the companion `retro-verse-1974-weekly-data.md`.
- `data/derived/cards/1974/retro-verse-1974-weekly-data.md` — Purpose: generated 1974 weekly narrative/context notes for cards. Key sections: `Movies`; `Cultural Textures`; `Mood Tags`; `TV References`; `Headline Tones`. Role: Supporting. Duplicates/conflicts: complements `1974_weekly_context.md`; generated data artifact, not policy documentation.

## CANONICAL DOCUMENTS

These files most clearly define rules or source-of-truth behavior:
- `docs/DATA_REGISTRY.md` for repository data schema, ownership, and dataset-path governance.
- `apps/magazine/retroverse-magazine/PROJECT_STATE.md` for magazine system rules, brand rules, issue structure, QA model, and directory expectations.
- `apps/magazine/retroverse-magazine/docs/CANONICAL_PIPELINE.md` for the intended magazine pipeline stage model and canonical inputs.
- `apps/magazine/retroverse-magazine/docs/ARCHITECTURE.md` for the magazine layer model and data flow.
- `apps/magazine/retroverse-magazine/charter/retroverse_editorial_charter.md` for contributor personas, voice rules, and editorial tone.
- `apps/magazine/retroverse-magazine/layout-library/docs/retroverse_layout_library.md` for template-selection, page-archetype, and composition rules.
- `apps/magazine/retroverse-magazine/layout-library/docs/page_rhythm_guide.md` for sequencing and pacing rules.
- `docs/RetroVerse Wheel Specification.md` for wheel-tier/color/animation rules.

Canonical caveat: several of these docs conflict with one another. In particular, `PROJECT_STATE.md`, `CANONICAL_PIPELINE.md`, the editorial charter, and the repair docs need consolidation into one updated source-of-truth set.

## SUPPORTING DOCUMENTS

Everything else is supporting material. The supporting set falls into these clusters:
- Repository migration/status docs: `TRUNK_STABILIZATION_*`, `MIGRATION_*`, `REPOSITORY_ARCHITECTURE_AUDIT.md`, `REGISTRY_PIPELINE_INTEGRATION.md`, `LINEAGE_AUTOMATION_REPORT.md`, `DATA_LINEAGE.md`.
- Magazine audits and repair reports: `PROJECT_AUDIT.md`, `MAGAZINE_PIPELINE_AUDIT.md`, `PROJECT_PIPELINE_REPORT.md`, `PRESS_CHECK_1978.md`, `PIPELINE_REPAIR_*`, `ISSUE_STRUCTURE_REPORT.md`, `SCREEN_CULTURE_*_AUDIT.md`.
- Workflow and QA artifacts: all `*_QA.md` files under `workflow/page_rebuild/output/` and `artifacts/output/1978/qa/`, plus `SINGLE_PAGE_REBUILD_REPORT.md`.
- Editorial planning and issue content: `issues/plans/1978_narrative_plan.md`, `issues/1978/layout/1978_issue_map.md`, page-source Markdown files, song pages, story drafts, and final story files.
- Archived/historical docs: archive READMEs, `archive/docs/Journal/rv_journal.md`, and the 1974 derived Markdown artifacts.

## REDUNDANT OR OUTDATED DOCUMENTS

High-confidence redundancy or drift:
- `README.md` is a stock Vite README and does not describe the actual repository.
- `docs/DATA_INVENTORY.md` and `apps/magazine/retroverse-magazine/DATA_INVENTORY.md` overlap each other and are both partly superseded by `docs/DATA_REGISTRY.md`.
- `docs/TRUNK_STABILIZATION_PLAN.md`, `docs/REPOSITORY_MIGRATION_SCRIPT.md`, and `docs/MIGRATION_VERIFICATION.md` are planning/preflight docs that were superseded by `docs/MIGRATION_EXECUTION_REPORT.md` and `docs/TRUNK_STABILIZATION_REPORT.md`.
- `docs/UNREGISTERED_DATASETS.md` is outdated because later registry docs show no remaining unregistered datasets.
- `apps/magazine/retroverse-magazine/PRESS_CHECK_1978.md` reflects a failing pre-repair state and conflicts with later passing QA artifacts.
- `apps/magazine/retroverse-magazine/PROJECT_AUDIT.md` is mostly an older fragmentation audit now overlapped by `MAGAZINE_PIPELINE_AUDIT.md`, `PROJECT_PIPELINE_REPORT.md`, and repair reports.
- `apps/magazine/retroverse-magazine/retroverse_1978_pilot.md` is a monolithic pilot draft superseded by the modular issue-page and article system.
- `apps/magazine/retroverse-magazine/prompts/generate_issue_prompt.md` and `apps/magazine/retroverse-magazine/templates/issue_template.md` are empty stubs.
- `apps/magazine/retroverse-magazine/issues/1978/arcade.md`, `ads.md`, `comic.md`, `puzzle1.md`, and `puzzle2.md` are placeholder-only content sources.
- Every draft story file under `apps/magazine/retroverse-magazine/issues/1978/articles/` is functionally duplicated by a final counterpart under `apps/magazine/retroverse-magazine/issues/1978/articles/final/`.

Important docs that are not redundant but are stale enough to require update:
- `apps/magazine/retroverse-magazine/docs/CANONICAL_PIPELINE.md`
- `apps/magazine/retroverse-magazine/PROJECT_STATE.md`
- `apps/magazine/retroverse-magazine/charter/retroverse_editorial_charter.md`
- `pipelines/support-data/README.md`

## PIPELINE DOCUMENTATION MAP

### Data
- `docs/DATA_REGISTRY.md`
- `docs/DATA_LINEAGE.md`
- `docs/DATA_REGISTRY_IMPLEMENTATION.md`
- `docs/REGISTRY_PIPELINE_INTEGRATION.md`
- `docs/TRUNK_STABILIZATION_REPORT.md`
- `docs/DATA_INVENTORY.md`
- `apps/magazine/retroverse-magazine/DATA_INVENTORY.md`
- `apps/magazine/retroverse-magazine/PROJECT_STATE.md`
- `apps/magazine/retroverse-magazine/docs/ARCHITECTURE.md`
- `apps/magazine/retroverse-magazine/docs/SCREEN_CULTURE_DATA_AUDIT.md`
- `apps/magazine/retroverse-magazine/docs/SCREEN_CULTURE_WAREHOUSE_AUDIT.md`
- `pipelines/support-data/README.md`

### Editorial
- `apps/magazine/retroverse-magazine/PROJECT_STATE.md`
- `apps/magazine/retroverse-magazine/charter/retroverse_editorial_charter.md`
- `apps/magazine/retroverse-magazine/issues/plans/1978_narrative_plan.md`
- `apps/magazine/retroverse-magazine/issues/1978/articles/*.md`
- `apps/magazine/retroverse-magazine/issues/1978/articles/final/*.md`
- `apps/magazine/retroverse-magazine/issues/1978/editor_letter.md`
- `apps/magazine/retroverse-magazine/issues/1978/charts_overview.md`
- `apps/magazine/retroverse-magazine/issues/1978/movies.md`
- `apps/magazine/retroverse-magazine/issues/1978/television.md`
- `apps/magazine/retroverse-magazine/issues/1978/culture.md`
- `apps/magazine/retroverse-magazine/issues/1978/letters.md`
- `apps/magazine/retroverse-magazine/issues/1978/songs/*.md`

### Art Direction
- `apps/magazine/retroverse-magazine/layout-library/docs/retroverse_layout_library.md`
- `apps/magazine/retroverse-magazine/layout-library/docs/page_rhythm_guide.md`
- `apps/magazine/retroverse-magazine/issues/1978/layout/1978_issue_map.md`
- `apps/magazine/retroverse-magazine/PIPELINE_REPAIR_IMPLEMENTATION.md`
- `apps/magazine/retroverse-magazine/workflow/page_rebuild/README.md`
- `apps/magazine/retroverse-magazine/workflow/page_rebuild/output/1978_movies_art_direction_QA.md`
- `apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_art_direction_QA.md`

### Illustration Generation
- `apps/magazine/retroverse-magazine/PROJECT_STATE.md`
- `apps/magazine/retroverse-magazine/PIPELINE_REPAIR_REPORT.md`
- `apps/magazine/retroverse-magazine/PIPELINE_REPAIR_IMPLEMENTATION.md`
- `apps/magazine/retroverse-magazine/MAGAZINE_PIPELINE_AUDIT.md`
- `apps/magazine/retroverse-magazine/workflow/page_rebuild/output/1978_movies_art_prompt_QA.md`
- `apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_art_prompt_QA.md`

### Layout
- `apps/magazine/retroverse-magazine/docs/CANONICAL_PIPELINE.md`
- `apps/magazine/retroverse-magazine/docs/ARCHITECTURE.md`
- `apps/magazine/retroverse-magazine/layout-library/docs/retroverse_layout_library.md`
- `apps/magazine/retroverse-magazine/layout-library/docs/page_rhythm_guide.md`
- `apps/magazine/retroverse-magazine/ISSUE_STRUCTURE_REPORT.md`
- `apps/magazine/retroverse-magazine/issues/1978/layout/1978_issue_map.md`
- `apps/magazine/retroverse-magazine/workflow/page_rebuild/output/1978_movies_layout_QA.md`
- `apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_layout_QA.md`

### Build
- `apps/magazine/retroverse-magazine/docs/CANONICAL_PIPELINE.md`
- `apps/magazine/retroverse-magazine/PIPELINE_REPAIR_REPORT.md`
- `apps/magazine/retroverse-magazine/PIPELINE_REPAIR_IMPLEMENTATION.md`
- `apps/magazine/retroverse-magazine/ISSUE_STRUCTURE_REPORT.md`
- `apps/magazine/retroverse-magazine/PRESS_CHECK_1978.md`
- `apps/magazine/retroverse-magazine/artifacts/output/1978/qa/1978_press_check_QA.md`
- `docs/TRUNK_STABILIZATION_REPORT.md`
- `docs/MIGRATION_EXECUTION_REPORT.md`

Cross-stage references that touch nearly the full pipeline:
- `apps/magazine/retroverse-magazine/docs/PROJECT_PIPELINE_REPORT.md`
- `apps/magazine/retroverse-magazine/MAGAZINE_PIPELINE_AUDIT.md`
- `docs/REPOSITORY_ARCHITECTURE_AUDIT.md`

## MISSING DOCUMENTATION

Obvious documentation gaps for the RetroVerse pipeline:
- A single current magazine source-of-truth doc that reconciles `PROJECT_STATE.md`, `CANONICAL_PIPELINE.md`, and the repair implementation with current paths and outputs.
- A formal schema/field contract for `issues/context/{year}_context.json` and the screen-culture provenance model used by editorial stages.
- A current CLI/operations README for the magazine orchestrator (`run_issue_pipeline.py` and related entrypoints), including inputs, outputs, flags, and failure modes.
- A schema doc for `1978_issue_map` and production-target artifacts, including who owns them and which stages consume them.
- A QA policy doc explaining each gate, pass/fail thresholds, blocking behavior, and the difference between single-page QA artifacts and issue-wide QA artifacts.
- A prompt/artifact contract for issue art prompts, image-prompt JSON, and illustration safe-zone rules.
- A repo-level README that explains the post-migration `/apps`, `/pipelines`, `/data`, `/archive`, and `/docs` structure.
- A single authoritative editorial staff/voice registry, since staff names currently drift across the project spec, charter, issue pages, and final bylines.
- Publication/deployment documentation for final magazine outputs, including where canonical HTML, PDF, and archived outputs should live after migration.
