#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translate GitHub repository descriptions into Simplified / Traditional Chinese.

A tiny zero-dependency tool (Python standard library only).

Examples:
    python translate.py facebook/react
    python translate.py https://github.com/facebook/react
    python translate.py --desc "A declarative UI library"
    python translate.py facebook/react --json

Optional environment variable:
    GITHUB_TOKEN=<your token>   # raises GitHub API rate limits (60/h -> 5000/h)
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

GITHUB_API = "https://api.github.com/repos/"
GOOGLE_API = "https://translate.googleapis.com/translate_a/single"
MYMEMORY_API = "https://api.mymemory.translated.net/get"
USER_AGENT = "gh-repo-desc-translator/1.0"


def http_get_json(url: str, headers: dict | None = None):
    """GET a URL and parse the JSON response."""
    request = urllib.request.Request(
        url, headers=headers or {"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_repo_description(repo: str) -> str:
    """Fetch the description of a GitHub repository via the public API."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        data = http_get_json(GITHUB_API + repo.strip("/"), headers)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            sys.exit(f"[error] Repository not found: {repo}")
        sys.exit(f"[error] GitHub API request failed: HTTP {exc.code}")
    except urllib.error.URLError as exc:
        sys.exit(f"[error] Network error: {exc.reason}")

    description = data.get("description")
    if not description:
        sys.exit(f"[error] Repository '{repo}' has no description to translate.")
    return description


def translate_google(text: str, target: str) -> str:
    """Translate via the free Google translate endpoint (no API key)."""
    params = {"client": "gtx", "sl": "auto", "tl": target, "dt": "t", "q": text}
    url = GOOGLE_API + "?" + urllib.parse.urlencode(params)
    data = http_get_json(url)
    return "".join(part[0] for part in data[0] if part and part[0])


def translate_mymemory(text: str, target: str) -> str:
    """Translate via the MyMemory free API (no API key, ~500 chars/request)."""
    params = {"q": text, "langpair": f"en|{target}"}
    url = MYMEMORY_API + "?" + urllib.parse.urlencode(params)
    data = http_get_json(url)
    if data.get("responseStatus") != 200:
        raise RuntimeError(f"MyMemory error: {data.get('responseDetails')}")
    translated = data.get("responseData", {}).get("translatedText", "")
    for line in translated.split("\n"):
        if "MYMEMORY WARNING" in line:
            continue  # skip the free-tier watermark line
        return line.strip()
    return translated.strip()


def translate(text: str, target: str, engine: str) -> str:
    """Translate text with the chosen engine; 'auto' falls back on failure."""
    if engine in ("auto", "google"):
        try:
            return translate_google(text, target)
        except Exception:
            if engine == "google":
                raise
    return translate_mymemory(text, target)


def parse_repo(value: str) -> str:
    """Accept 'owner/repo' or a full GitHub URL and return 'owner/repo'."""
    value = value.strip()
    if value.startswith(("http://", "https://")):
        path = urllib.parse.urlparse(value).path.strip("/")
        parts = path.split("/")
        if len(parts) >= 2:
            return "/".join(parts[:2])
        sys.exit("[error] Not a valid GitHub repository URL.")
    if value.count("/") == 1:
        return value
    sys.exit("[error] Expected 'owner/repo' or a GitHub repository URL.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Translate a GitHub repository description into zh-CN and zh-TW."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "repo",
        nargs="?",
        help="GitHub repo, e.g. owner/repo or https://github.com/owner/repo",
    )
    group.add_argument(
        "--desc",
        help="Translate a description text directly instead of fetching from GitHub",
    )
    parser.add_argument(
        "--engine",
        choices=["auto", "google", "mymemory"],
        default="auto",
        help="Translation engine: auto (google first, fallback mymemory), google, or mymemory",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    text = args.desc if args.desc else fetch_repo_description(parse_repo(args.repo))

    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        zh_cn = translate(text, "zh-CN", args.engine)
        zh_tw = translate(text, "zh-TW", args.engine)
    except urllib.error.URLError as exc:
        sys.exit(f"[error] Translation request failed: {exc.reason}")
    except Exception as exc:
        sys.exit(f"[error] Translation failed: {exc}")

    if args.json:
        print(
            json.dumps(
                {"original": text, "zh-CN": zh_cn, "zh-TW": zh_tw},
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    print(f"Original (EN): {text}")
    print(f"简体中文 (zh-CN): {zh_cn}")
    print(f"繁體中文 (zh-TW): {zh_tw}")


if __name__ == "__main__":
    main()
