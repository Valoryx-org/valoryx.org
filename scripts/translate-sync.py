#!/usr/bin/env python3
"""
Translation sync pipeline for Valoryx Hugo site.

English (i18n/en.toml) is the single source of truth.
This script detects which English keys changed and manages the TOML files.
Translation is done by Claude Opus running locally — no external API needed.

Workflow:
  1. detect  → find changed/new/deleted keys, output JSON to pending-translations.json
  2. apply   → read completed-translations.json, update all target TOML files

How Claude uses this:
  1. Run:   python scripts/translate-sync.py detect
  2. Read:  pending-translations.json (keys needing translation)
  3. Claude translates all keys to 5 languages
  4. Write: completed-translations.json
  5. Run:   python scripts/translate-sync.py apply
  6. Done — all TOML files updated, checksums saved

Usage:
  python scripts/translate-sync.py detect           # find changes, write pending-translations.json
  python scripts/translate-sync.py detect --force   # treat ALL keys as changed
  python scripts/translate-sync.py apply            # apply completed-translations.json to TOML files
  python scripts/translate-sync.py status           # show current sync status (no changes)
"""

import hashlib
import json
import re
import sys
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

SITE_DIR = Path(__file__).parent.parent
I18N_DIR = SITE_DIR / "i18n"
CHECKSUMS_FILE = SITE_DIR / ".i18n-checksums.json"
PENDING_FILE = SITE_DIR / "pending-translations.json"
COMPLETED_FILE = SITE_DIR / "completed-translations.json"
SOURCE_LANG = "en"
TARGET_LANGS = ["fr", "de", "es", "ru", "uk"]

LANG_NAMES = {
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian",
    "uk": "Ukrainian",
}

# ── TOML Parser ───────────────────────────────────────────────────────────────

def parse_toml_keys(filepath: Path) -> dict[str, str]:
    """Parse Hugo i18n TOML → {key: value} dict."""
    keys = {}
    current_key = None
    for line in filepath.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^\[([a-zA-Z0-9_]+)\]', line)
        if m:
            current_key = m.group(1)
            continue
        if current_key:
            m = re.match(r'^other\s*=\s*"(.*)"$', line)
            if m:
                keys[current_key] = m.group(1)
                current_key = None
    return keys


def update_toml_values(filepath: Path, updates: dict[str, str], deletions: set[str] | None = None):
    """Update specific keys in TOML file, preserving structure and comments."""
    lines = filepath.read_text(encoding="utf-8").splitlines()
    result = []
    current_key = None
    skip_block = False
    i = 0

    while i < len(lines):
        line = lines[i]
        m = re.match(r'^\[([a-zA-Z0-9_]+)\]', line)
        if m:
            key = m.group(1)
            if deletions and key in deletions:
                skip_block = True
                i += 1
                continue
            skip_block = False
            current_key = key
            result.append(line)
            i += 1
            continue

        if skip_block:
            i += 1
            continue

        if current_key and current_key in updates:
            m2 = re.match(r'^other\s*=\s*"', line)
            if m2:
                result.append(f'other = "{updates[current_key]}"')
                current_key = None
                i += 1
                continue

        result.append(line)
        i += 1

    # Append new keys not already in file
    existing = set()
    for line in result:
        m = re.match(r'^\[([a-zA-Z0-9_]+)\]', line)
        if m:
            existing.add(m.group(1))

    new_keys = set(updates.keys()) - existing
    if new_keys:
        result.append("")
        result.append("# ── Auto-translated (new keys) ─────────────────────────────────────────────")
        for key in sorted(new_keys):
            result.append(f"[{key}]")
            result.append(f'other = "{updates[key]}"')

    filepath.write_text("\n".join(result) + "\n", encoding="utf-8")


# ── Checksum tracking ─────────────────────────────────────────────────────────

def compute_checksums(keys: dict[str, str]) -> dict[str, str]:
    return {k: hashlib.sha256(v.encode()).hexdigest()[:16] for k, v in keys.items()}

def load_checksums() -> dict[str, str]:
    if CHECKSUMS_FILE.exists():
        return json.loads(CHECKSUMS_FILE.read_text(encoding="utf-8"))
    return {}

def save_checksums(checksums: dict[str, str]):
    CHECKSUMS_FILE.write_text(json.dumps(checksums, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_detect(force: bool = False):
    """Detect changed English keys and write pending-translations.json."""
    en_keys = parse_toml_keys(I18N_DIR / f"{SOURCE_LANG}.toml")
    new_checksums = compute_checksums(en_keys)
    old_checksums = {} if force else load_checksums()

    changed = {}
    new = {}
    deleted = set(old_checksums.keys()) - set(new_checksums.keys())

    for key, checksum in new_checksums.items():
        if key not in old_checksums:
            new[key] = en_keys[key]
        elif old_checksums[key] != checksum:
            changed[key] = en_keys[key]

    to_translate = {**changed, **new}

    print(f"English keys: {len(en_keys)}")
    print(f"Changed: {len(changed)}  New: {len(new)}  Deleted: {len(deleted)}")
    print(f"Total to translate: {len(to_translate)}")

    if not to_translate and not deleted:
        print("\nAll translations are up to date.")
        return

    # Write pending file for Claude to read
    pending = {
        "source_lang": SOURCE_LANG,
        "target_langs": TARGET_LANGS,
        "lang_names": LANG_NAMES,
        "to_translate": to_translate,
        "deleted": sorted(deleted),
        "instructions": (
            "Translate each key from English to all 5 target languages. "
            "Preserve HTML tags exactly. Keep technical terms (git, MCP, Docker, API, CLI, WYSIWYG, RBAC, JWT). "
            "Never translate brand names (Valoryx, DocPlatform). Keep pricing numbers exact ($0, $29, $79). "
            "Translate precisely (preserve meaning) while reading naturally in each language."
        ),
    }

    PENDING_FILE.write_text(json.dumps(pending, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nWrote {PENDING_FILE.name} — {len(to_translate)} keys need translation")
    print(f"\nClaude: read {PENDING_FILE.name}, translate, write {COMPLETED_FILE.name}")
    print(f"Format: {{ \"fr\": {{key: value}}, \"de\": {{...}}, ... }}")


def cmd_apply():
    """Apply completed translations from completed-translations.json."""
    if not COMPLETED_FILE.exists():
        print(f"ERROR: {COMPLETED_FILE.name} not found. Run 'detect' first, then translate.")
        sys.exit(1)

    completed = json.loads(COMPLETED_FILE.read_text(encoding="utf-8"))

    # Load pending to get deletion list
    deleted = set()
    if PENDING_FILE.exists():
        pending = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        deleted = set(pending.get("deleted", []))

    for lang in TARGET_LANGS:
        if lang not in completed:
            print(f"WARNING: {lang} not in completed translations, skipping")
            continue

        lang_file = I18N_DIR / f"{lang}.toml"
        translations = completed[lang]
        update_toml_values(lang_file, translations, deleted)
        print(f"  Updated {lang}.toml: {len(translations)} keys")

    if deleted:
        print(f"  Deleted {len(deleted)} obsolete keys from all languages")

    # Update checksums
    en_keys = parse_toml_keys(I18N_DIR / f"{SOURCE_LANG}.toml")
    save_checksums(compute_checksums(en_keys))

    # Clean up temp files
    PENDING_FILE.unlink(missing_ok=True)
    COMPLETED_FILE.unlink(missing_ok=True)

    print(f"\nChecksums saved. Temp files cleaned. Done.")


def cmd_status():
    """Show current sync status."""
    en_keys = parse_toml_keys(I18N_DIR / f"{SOURCE_LANG}.toml")
    new_checksums = compute_checksums(en_keys)
    old_checksums = load_checksums()

    changed = sum(1 for k, v in new_checksums.items() if k in old_checksums and old_checksums[k] != v)
    new = sum(1 for k in new_checksums if k not in old_checksums)
    deleted = sum(1 for k in old_checksums if k not in new_checksums)

    print(f"English keys: {len(en_keys)}")
    print(f"Changed: {changed}  New: {new}  Deleted: {deleted}")

    if changed + new + deleted == 0:
        print("Status: ALL IN SYNC")
    else:
        print(f"Status: {changed + new + deleted} keys need attention → run 'detect'")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: translate-sync.py <detect|apply|status> [--force]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "detect":
        cmd_detect(force="--force" in sys.argv)
    elif command == "apply":
        cmd_apply()
    elif command == "status":
        cmd_status()
    else:
        print(f"Unknown command: {command}")
        print("Usage: translate-sync.py <detect|apply|status> [--force]")
        sys.exit(1)


if __name__ == "__main__":
    main()
