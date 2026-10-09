#!/usr/bin/env python3
"""
Resolve the emulator registry from a hand-maintained source list.

Design (Option A): the primary update key is the release **tag / versionName**,
read from GitHub release metadata. We never download an APK — so this stays cheap
even for huge emulators (e.g. GameNative is 560 MB). For each `github` source we
hit the Releases API (authenticated, 5000 req/hr) to resolve:

  - latest_version_name  <- release tag (leading "v" stripped)
  - published_at         <- release publish time
  - download_url         <- the asset whose name matches `asset_regex`

`gitlab` and `gitea` sources resolve the latest release from those forges' REST
APIs (for emulators that left GitHub — e.g. Switch forks); both emit a `direct`
source. A `http_index` source resolves the newest version from a buildbot-style
HTTP directory listing (e.g. RetroArch's buildbot.libretro.com/stable/) and
builds a direct APK URL — also no APK download. `play_store` / static `direct`
sources need no network. Output is written
as emulators-<registry_version>.json + info.json, matching the schema the app's
EmulatorRegistryClient / EmulatorRegistryGatewayAdapter expect.

Usage:
  resolve.py --sources tools/emulator-registry/sources.json \
             --out app/src/main/assets/emulators \
             [--registry-version 1] [--strict]
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

GITHUB_API = "https://api.github.com"
USER_AGENT = "console-launcher-emulator-registry"


def log(msg):
    print(msg, file=sys.stderr)


def retry(fn, attempts=3, base_delay=2):
    """Run fn with retries on transient failures. A 404 is not transient and is
    re-raised immediately so callers can treat it as 'no such release'."""
    last = None
    for i in range(attempts):
        try:
            return fn()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            last = e
        except Exception as e:  # noqa: BLE001 - network is best-effort
            last = e
        time.sleep(base_delay * (i + 1))
    raise last


def gh_request(url):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    def do():
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)

    return retry(do)


def latest_release(repo):
    """Latest published (non-draft) release, falling back to the newest of all
    releases when a repo only ships prereleases (so /latest 404s)."""
    try:
        return gh_request(f"{GITHUB_API}/repos/{repo}/releases/latest")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    releases = gh_request(f"{GITHUB_API}/repos/{repo}/releases?per_page=10")
    for rel in releases:
        if not rel.get("draft"):
            return rel
    return None


def head_ok(url):
    """True if the URL responds 200 with an APK content type (best-effort)."""
    def do():
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            ctype = resp.headers.get("Content-Type", "")
            return resp.status == 200 and (
                "android.package-archive" in ctype or "octet-stream" in ctype or url.endswith(".apk")
            )
    try:
        return retry(do)
    except urllib.error.HTTPError as e:
        log(f"    ! HEAD {url} -> {e.code}")
        return False
    except Exception as e:  # noqa: BLE001 - network best-effort
        log(f"    ! HEAD {url} -> {e}")
        return False


def http_get_text(url):
    def do():
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", "replace")
    return retry(do)


def version_key(v):
    """Sort key from the integer runs in a version string (so 1.22.2 > 1.9.14)."""
    return tuple(int(x) for x in re.findall(r"\d+", v)) or (0,)


def strip_v(tag):
    return re.sub(r"^v(?=\d)", "", tag.strip())


def resolve_github(entry, warnings):
    """Resolve version + APK URL from a GitHub repo's latest release.

    Two modes:
      - asset_regex: pick the matching APK asset attached to the release (the
        common case — the APK lives on GitHub).
      - apk_template: the release only gives us the version; the APK lives on an
        external site at a predictable URL. Build it from the tag, substituting
        {version} (v-stripped) and {version_us} (dots -> underscores), and emit a
        `direct` source. E.g. PPSSPP: hrydgard/ppsspp tag -> ppsspp.org/files/.

    Returns (source_dict_or_None, version_name, published_at).
    """
    cfg = entry["github"]
    repo = cfg["repo"]
    abi = cfg.get("abi")
    template = cfg.get("apk_template")
    tag_pin = cfg.get("tag")  # pin to a specific (e.g. rolling "nightly") tag
    log(f"  github: {repo} ({'template' if template else 'asset ~ /' + cfg.get('asset_regex', '') + '/'}{', tag=' + tag_pin if tag_pin else ''})")

    if tag_pin:
        try:
            rel = gh_request(f"{GITHUB_API}/repos/{repo}/releases/tags/{tag_pin}")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
            rel = None
    else:
        rel = latest_release(repo)
    if not rel:
        warnings.append(f"{entry['id']}: no usable release on {repo}")
        return None, None, None

    version = strip_v(rel.get("tag_name", ""))
    published = rel.get("published_at")

    if template:
        url = template.format(version=version, version_us=version.replace(".", "_"))
        if not head_ok(url):
            warnings.append(f"{entry['id']}: templated download_url failed HEAD check: {url}")
        source = {"type": "direct", "download_url": url}
        if abi:
            source["abi"] = abi
        return source, version, published

    asset_regex = cfg["asset_regex"]
    pattern = re.compile(asset_regex)
    asset = next((a for a in rel.get("assets", []) if pattern.search(a["name"])), None)
    if not asset:
        names = ", ".join(a["name"] for a in rel.get("assets", [])) or "(none)"
        warnings.append(f"{entry['id']}: no asset matched /{asset_regex}/ in {rel.get('tag_name')} [{names}]")
        return None, version, published

    url = asset["browser_download_url"]
    if not head_ok(url):
        warnings.append(f"{entry['id']}: download_url failed HEAD check: {url}")

    source = {"type": "github_release", "repo": repo, "asset_regex": asset_regex, "download_url": url}
    if abi:
        source["abi"] = abi
    return source, version, published


def gitlab_latest_release(project):
    enc = urllib.parse.quote(project, safe="")
    token = os.environ.get("GITLAB_TOKEN")

    def do():
        url = f"https://gitlab.com/api/v4/projects/{enc}/releases?per_page=10"
        headers = {"User-Agent": USER_AGENT}
        if token:
            headers["PRIVATE-TOKEN"] = token
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)

    rels = retry(do)
    for rel in rels:
        if not rel.get("upcoming_release"):
            return rel
    return rels[0] if rels else None


def resolve_gitlab(entry, warnings):
    """Resolve version + APK URL from a GitLab project's latest release.
    GitLab release assets are 'links'; we use their direct_asset_url permalink."""
    cfg = entry["gitlab"]
    project = cfg["project"]
    log(f"  gitlab: {project} (asset ~ /{cfg['asset_regex']}/)")
    rel = gitlab_latest_release(project)
    if not rel:
        warnings.append(f"{entry['id']}: no release on gitlab {project}")
        return None, None, None

    version = strip_v(rel.get("tag_name", ""))
    published = rel.get("released_at")
    links = (rel.get("assets") or {}).get("links") or []
    pattern = re.compile(cfg["asset_regex"])
    link = next((l for l in links if pattern.search(l.get("name", ""))), None)
    if not link:
        names = ", ".join(l.get("name", "") for l in links) or "(none)"
        warnings.append(f"{entry['id']}: no gitlab asset matched /{cfg['asset_regex']}/ in {rel.get('tag_name')} [{names}]")
        return None, version, published

    url = link.get("direct_asset_url") or link.get("url")
    if not head_ok(url):
        warnings.append(f"{entry['id']}: gitlab download_url failed HEAD check: {url}")
    source = {"type": "direct", "download_url": url}
    if cfg.get("abi"):
        source["abi"] = cfg["abi"]
    return source, version, published


def gitea_latest_release(base, repo):
    def fetch(url):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)

    try:
        return retry(lambda: fetch(f"{base}/api/v1/repos/{repo}/releases/latest"))
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    rels = retry(lambda: fetch(f"{base}/api/v1/repos/{repo}/releases?limit=10"))
    for rel in rels:
        if not rel.get("draft") and not rel.get("prerelease"):
            return rel
    return rels[0] if rels else None


def resolve_gitea(entry, warnings):
    """Resolve version + APK URL from a Gitea instance's latest release
    (same asset shape as GitHub). E.g. eden on git.eden-emu.dev."""
    cfg = entry["gitea"]
    base = cfg["base"].rstrip("/")
    repo = cfg["repo"]
    log(f"  gitea: {base}/{repo} (asset ~ /{cfg['asset_regex']}/)")
    rel = gitea_latest_release(base, repo)
    if not rel:
        warnings.append(f"{entry['id']}: no release on gitea {base}/{repo}")
        return None, None, None

    version = strip_v(rel.get("tag_name", ""))
    published = rel.get("published_at")
    assets = rel.get("assets") or []
    pattern = re.compile(cfg["asset_regex"])
    asset = next((a for a in assets if pattern.search(a.get("name", ""))), None)
    if not asset:
        names = ", ".join(a.get("name", "") for a in assets) or "(none)"
        warnings.append(f"{entry['id']}: no gitea asset matched /{cfg['asset_regex']}/ in {rel.get('tag_name')} [{names}]")
        return None, version, published

    url = asset.get("browser_download_url")
    if not head_ok(url):
        warnings.append(f"{entry['id']}: gitea download_url failed HEAD check: {url}")
    source = {"type": "direct", "download_url": url}
    if cfg.get("abi"):
        source["abi"] = cfg["abi"]
    return source, version, published


def resolve_http_index(entry, warnings):
    """Resolve the newest version from an HTTP directory listing (buildbot-style)
    and build a direct APK URL from a template. Returns (direct_source, version)."""
    cfg = entry["http_index"]
    log(f"  http_index: {cfg['index_url']} (link ~ /{cfg['link_regex']}/)")
    html = http_get_text(cfg["index_url"])
    versions = sorted({m for m in re.findall(cfg["link_regex"], html)}, key=version_key)
    if not versions:
        warnings.append(f"{entry['id']}: no versions matched /{cfg['link_regex']}/ at {cfg['index_url']}")
        return None, None

    version = versions[-1]
    url = cfg["apk_template"].format(version=version)
    if not head_ok(url):
        warnings.append(f"{entry['id']}: index download_url failed HEAD check: {url}")

    source = {"type": "direct", "download_url": url}
    if cfg.get("abi"):
        source["abi"] = cfg["abi"]
    return source, version


def build_entry(entry, warnings):
    sources = []
    version_name = entry.get("version_name")  # optional manual override / non-github
    published_at = entry.get("published_at")

    if "github" in entry:
        try:
            gh_source, gh_version, gh_published = resolve_github(entry, warnings)
        except Exception as e:  # noqa: BLE001 - never let one repo abort the run
            warnings.append(f"{entry['id']}: github resolution failed: {e}")
            gh_source, gh_version, gh_published = None, None, None
        if gh_source:
            sources.append(gh_source)
        if gh_version:
            version_name = gh_version
        if gh_published:
            published_at = gh_published

    for forge, resolver in (("gitlab", resolve_gitlab), ("gitea", resolve_gitea)):
        if forge in entry:
            try:
                f_source, f_version, f_published = resolver(entry, warnings)
            except Exception as e:  # noqa: BLE001 - never let one host abort the run
                warnings.append(f"{entry['id']}: {forge} resolution failed: {e}")
                f_source, f_version, f_published = None, None, None
            if f_source:
                sources.append(f_source)
            if f_version and not version_name:
                version_name = f_version
            if f_published and not published_at:
                published_at = f_published

    if "http_index" in entry:
        try:
            idx_source, idx_version = resolve_http_index(entry, warnings)
        except Exception as e:  # noqa: BLE001 - never let one host abort the run
            warnings.append(f"{entry['id']}: http_index resolution failed: {e}")
            idx_source, idx_version = None, None
        if idx_source:
            sources.append(idx_source)
        if idx_version and not version_name:
            version_name = idx_version

    if "direct" in entry:
        d = entry["direct"]
        src = {"type": "direct", "download_url": d["url"]}
        if d.get("abi"):
            src["abi"] = d["abi"]
        sources.append(src)

    if entry.get("play_store"):
        sources.append({
            "type": "play_store",
            "url": f"https://play.google.com/store/apps/details?id={entry['package_name']}",
        })

    out = {
        "id": entry["id"],
        "package_name": entry["package_name"],
        "display_name": entry["display_name"],
    }
    if entry.get("publisher"):
        out["publisher"] = entry["publisher"]
    # NB: entry-level "abis" is intentionally NOT emitted — the app derives it from
    # each source's "abi" (EmulatorRegistryEntry.abis is a computed property).
    if version_name:
        out["latest_version_name"] = version_name
    if published_at:
        out["published_at"] = published_at
    out["sources"] = sources

    if not sources:
        warnings.append(f"{entry['id']}: no sources resolved (entry will be inert)")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", required=True)
    ap.add_argument("--out", required=True, help="output directory for emulators-N.json + info.json")
    ap.add_argument("--registry-version", type=int, default=1)
    ap.add_argument("--strict", action="store_true", help="exit non-zero if any warnings")
    args = ap.parse_args()

    with open(args.sources, encoding="utf-8") as f:
        entries = json.load(f)

    warnings = []
    resolved = []
    for entry in entries:
        log(f"- {entry['id']} ({entry['package_name']})")
        resolved.append(build_entry(entry, warnings))

    os.makedirs(args.out, exist_ok=True)
    reg_path = os.path.join(args.out, f"emulators-{args.registry_version}.json")
    info_path = os.path.join(args.out, "info.json")
    with open(reg_path, "w", encoding="utf-8") as f:
        json.dump(resolved, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump({"registry_version": args.registry_version}, f, indent=2)
        f.write("\n")

    log("")
    log(f"Wrote {len(resolved)} emulators -> {reg_path}")
    gh_count = sum(1 for e in resolved if any(s["type"] == "github_release" for s in e["sources"]))
    log(f"  github_release sources resolved: {gh_count}")
    if warnings:
        log(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            log(f"  - {w}")
        if args.strict:
            sys.exit(1)


if __name__ == "__main__":
    main()
