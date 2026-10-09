# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is **not an application codebase** — it's a content/asset repository served via `raw.githubusercontent.com` to the Console Launcher Android app (Play Store: `com.k2.consolelauncher`). There is no build system, test suite, or runtime. Changes are validated by editing JSON and shipping it; the live app fetches it directly.

The app fetches indexes from hardcoded URLs of the form `https://raw.githubusercontent.com/likeich/console-launcher/main/<area>/<index>.json`. Renaming or moving a top-level directory or its index file is a breaking change for shipped clients.

## Top-level layout and what each area serves

- **`platforms/`** — emulator/console definitions. Each `<Platform>.json` declares scrapers, file regexes, and a `playerList` of emulator launch configs. `index.json` lists every platform with a `revisionNumber` the client uses to detect updates. The app loads this from `platforms/index.json`. **Users can override the URL** in *Settings > Frontend > Platform Settings*.
- **`themes/`** — the active theming system. `themes/index.json` is the entry point and points to sub-indexes for `dock/`, `startup/`, `icons/`, `wallpaper-packs/`, `ui-skins/`, and `meta-themes/`. Each subdirectory has a `packs.json` (or `themes.json` for icons) listing its packs, plus a `pack-template.json` showing the schema for a new pack. `meta-themes/packs.json` composes other packs together (it references `dockPack`, `uiPack`, `wallpaperPack`, `iconPack`, `startupPack` IDs that must exist in their respective indexes).
- **`dock-themes/`** — legacy dock icon packs at the repo root, still referenced by older client versions via `dock-themes/packs.json`. The current equivalent is `themes/dock/`. Keep both in sync when adding dock packs unless intentionally dropping legacy support.
- **`market/`** — Console Market, a curated app/game directory. `info.json` carries `database_version` (bump when content shape changes); `content-N.json` files hold entries. `contributing.md` lists requested additions.
- **`content/`** — long-form Markdown tutorials shown in-app (`tutorial.md`, `ra-tutorial.md`).
- **`scripts/`** — local utilities (not run by CI). `video_to_square_webp.py` converts a video to a centered 1:1 animated WebP via `ffmpeg` (used for wallpaper/dock animations).
- **`readme-assets/`** — images for the GitHub README only; not consumed by the app.

## Working with this repo

- **No build, lint, or tests.** Validate JSON edits with a JSON parser (`python3 -m json.tool < file.json` or similar) before committing. Malformed JSON ships immediately to users on the next fetch.
- **Bump `revisionNumber`** in `platforms/index.json` (and `databaseVersion`/`revisionNumber` inside the per-platform file) when changing a platform definition — clients use it to decide whether to re-pull.
- **Cross-reference IDs**: when adding a meta-theme variant, its `wallpaperPack` / `dockPack` / `uiPack` / `iconPack` / `startupPack` slugs must exist in the corresponding `packs.json`. Same for any new entries in `themes/themes.json` (the legacy top-level theme list).
- **`market/content-1.json`** entries follow a fixed schema: `name`, `category` (array), `sources` (array of URLs), `price`, `price_description`, `controller_support`, `image`. New games should be controller-friendly per `market/contributing.md`.

## Platform sync workflow (the one piece of automation)

`.github/workflows/sync-platforms.yml` (`workflow_dispatch` only, manually triggered) pulls the entire `platforms/` directory from `magneticchen/Daijishou`, rewrites `baseUri` to point at this repo, then re-applies overlays from `platforms/custom-players.json` — a list of `{file, insertAfter, player}` entries that inject extra emulator launch configs into the upstream platform files (e.g. the `Drastic (RG DS)` and `GameNative (PcGame)` players). The workflow preserves `platforms/README.md`, `custom-players.json`, and `.gitignore` across the wipe-and-restore.

When adding a custom emulator entry that should survive future syncs, **add it to `custom-players.json` — do not edit the platform JSON directly**, or the next sync will erase it.
