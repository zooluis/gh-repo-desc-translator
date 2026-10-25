#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translate GitHub repository descriptions into Simplified / Traditional Chinese.

A tiny zero-dependency tool (Python standard library only).

Examples:
    python translate.py facebook/react
    python translate.py https://github.com/facebook/react
    python translate.py --desc "A declarative UI library"
    python translate.py facebook/react --json
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

GITHUB_API = "https://api.github.com/repos/"
TRANSLATE_API = "https://translate.googleapis.com/translate_a/single"
USER_AGENT = "gh-repo-desc-translator/1.0"


def fetch_repo_description(repo: str) -> str:
    """Fetch the description of a GitHub repository via the public API."""
    url = GITHUB_API + repo.strip("/")
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
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


def translate(text: str, target: str) -> str:
    """Translate text to the target language via the free Google translate endpoint."""
    params = {"client": "gtx", "sl": "auto", "tl": target, "dt": "t", "q": text}
    url = TRANSLATE_API + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        sys.exit(f"[error] Translation request failed: {exc.reason}")
    return "".join(part[0] for part in data[0] if part and part[0])


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
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    text = args.desc if args.desc else fetch_repo_description(parse_repo(args.repo))

    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    zh_cn = translate(text, "zh-CN")
    zh_tw = translate(text, "zh-TW")

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
