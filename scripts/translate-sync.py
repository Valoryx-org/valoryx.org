#!/usr/bin/env python3
"""
Auto-translation pipeline for Valoryx Hugo site.

English (i18n/en.toml) is the single source of truth for all i18n keys.
This script detects which English keys changed since last sync, translates
them to all target languages, and updates the TOML files.

How it works:
  1. Parse en.toml → extract all [key] + other = "value" pairs
  2. Load .i18n-checksums.json → SHA-256 of each English value from last sync
  3. Compare → find changed, new, and deleted keys
  4. Batch-translate changed/new keys using OpenRouter API (Claude Haiku)
  5. Update each target language TOML with new translations
  6. Save updated checksums

Translation quality:
  - Uses Claude Haiku via OpenRouter (~$0.001 per batch) for natural marketing copy
  - Falls back to copying English with [EN] prefix if no API key available
  - Preserves existing translations for unchanged keys
  - Maintains TOML structure, comments, and ordering

Usage:
  python scripts/translate-sync.py              # auto-detect and translate changes
  python scripts/translate-sync.py --force      # retranslate ALL keys
  python scripts/translate-sync.py --dry-run    # show what would change without modifying files

Requires:
  OPENROUTER_API_KEY env var (or set in .env)
  pip install requests (usually pre-installed)
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Install: pip install requests")
    sys.exit(1)

# ── Configuration ─────────────────────────────────────────────────────────────

SITE_DIR = Path(__file__).parent.parent
I18N_DIR = SITE_DIR / "i18n"
CHECKSUMS_FILE = SITE_DIR / ".i18n-checksums.json"
SOURCE_LANG = "en"
TARGET_LANGS = ["fr", "de", "es", "ru", "uk"]

LANG_NAMES = {
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian",
    "uk": "Ukrainian",
}

# Keys that should NEVER be translated (brand names, technical terms)
SKIP_KEYS = {
    "nav_home",  # "Home" is sometimes kept in English intentionally
}

# Max keys per translation API call (to avoid token limits)
BATCH_SIZE = 40

# ── TOML Parser (simple, no external dependency) ─────────────────────────────

def parse_toml_keys(filepath: Path) -> dict[str, str]:
    """Parse Hugo i18n TOML file → {key: value} dict.

    Format:
      [key_name]
      other = "value with \\"escapes\\""
    """
    keys = {}
    current_key = None

    for line in filepath.read_text(encoding="utf-8").splitlines():
        # Match [key_name]
        m = re.match(r'^\[([a-zA-Z0-9_]+)\]', line)
        if m:
            current_key = m.group(1)
            continue

        # Match other = "value"
        if current_key:
            m = re.match(r'^other\s*=\s*"(.*)"$', line)
            if m:
                keys[current_key] = m.group(1)
                current_key = None

    return keys


def update_toml_values(filepath: Path, updates: dict[str, str], deletions: set[str] | None = None):
    """Update specific keys in a TOML file, preserving structure and comments.

    Also removes keys that no longer exist in English (if deletions provided).
    """
    lines = filepath.read_text(encoding="utf-8").splitlines()
    result = []
    current_key = None
    skip_until_next_key = False
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for [key_name]
        m = re.match(r'^\[([a-zA-Z0-9_]+)\]', line)
        if m:
            key = m.group(1)

            # If this key was deleted from English, skip it and its value line
            if deletions and key in deletions:
                skip_until_next_key = True
                i += 1
                continue

            skip_until_next_key = False
            current_key = key
            result.append(line)
            i += 1
            continue

        if skip_until_next_key:
            i += 1
            continue

        # Check for other = "value" line under a key we want to update
        if current_key and current_key in updates:
            m2 = re.match(r'^other\s*=\s*"', line)
            if m2:
                # Replace the value
                escaped = updates[current_key].replace('\\', '\\\\').replace('"', '\\"')
                # But don't double-escape things that are already escaped in the source
                # (like HTML class attributes in br tags)
                result.append(f'other = "{updates[current_key]}"')
                current_key = None
                i += 1
                continue

        result.append(line)
        i += 1

    # Append any new keys that weren't in the file
    existing_keys = set()
    for line in result:
        m = re.match(r'^\[([a-zA-Z0-9_]+)\]', line)
        if m:
            existing_keys.add(m.group(1))

    new_keys = set(updates.keys()) - existing_keys
    if new_keys:
        result.append("")
        result.append("# ── Auto-translated (new keys) ─────────────────────────────────────────────")
        for key in sorted(new_keys):
            result.append(f"[{key}]")
            result.append(f'other = "{updates[key]}"')

    filepath.write_text("\n".join(result) + "\n", encoding="utf-8")


# ── Checksum tracking ─────────────────────────────────────────────────────────

def compute_checksums(keys: dict[str, str]) -> dict[str, str]:
    """Compute SHA-256 for each key's English value."""
    return {k: hashlib.sha256(v.encode()).hexdigest()[:16] for k, v in keys.items()}


def load_checksums() -> dict[str, str]:
    """Load previous checksums from file."""
    if CHECKSUMS_FILE.exists():
        return json.loads(CHECKSUMS_FILE.read_text(encoding="utf-8"))
    return {}


def save_checksums(checksums: dict[str, str]):
    """Save checksums to file."""
    CHECKSUMS_FILE.write_text(
        json.dumps(checksums, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )


# ── Translation via OpenRouter API ────────────────────────────────────────────

def get_api_key() -> str | None:
    """Get OpenRouter API key from env or .env file."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key

    env_file = SITE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"')

    return None


def translate_batch(keys_values: dict[str, str], target_lang: str, api_key: str) -> dict[str, str]:
    """Translate a batch of English i18n keys to target language using Claude Haiku.

    Returns {key: translated_value} dict.
    """
    lang_name = LANG_NAMES.get(target_lang, target_lang)

    # Build the translation prompt
    entries = "\n".join(f"  {k}: {v}" for k, v in keys_values.items())

    prompt = f"""Translate these Hugo i18n strings from English to {lang_name}.

Rules:
- Translate PRECISELY — preserve the exact meaning, not a creative rewrite
- The result must read naturally in {lang_name} — not word-for-word but sense-for-sense
- Preserve ALL HTML tags exactly (like <br class=\\"hidden sm:block\\">)
- Preserve technical terms: git, MCP, Docker, WYSIWYG, API, CLI, RBAC, JWT, OIDC
- Brand name "Valoryx" and "DocPlatform" are NEVER translated
- Preserve escape sequences (backslashes before quotes)
- For pricing: keep exact numbers ($0, $29, $79)
- Keep the same tone: professional, developer-friendly, concise

Input (key: English value):
{entries}

Output ONLY a valid JSON object mapping key to translated value. No explanation, no markdown, just JSON:
"""

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "anthropic/claude-haiku-4-5-20251001",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 4096,
            },
            timeout=60,
        )
        resp.raise_for_status()

        content = resp.json()["choices"][0]["message"]["content"].strip()

        # Extract JSON from response (handle markdown code blocks)
        if content.startswith("```"):
            content = re.sub(r'^```\w*\n?', '', content)
            content = re.sub(r'\n?```$', '', content)

        return json.loads(content)

    except Exception as e:
        print(f"  WARNING: Translation API failed for {lang_name}: {e}")
        return {}


def fallback_translate(keys_values: dict[str, str]) -> dict[str, str]:
    """Fallback: copy English with [EN] prefix when no API key available."""
    return {k: f"[EN] {v}" for k, v in keys_values.items()}


# ── Main pipeline ─────────────────────────────────────────────────────────────

def main():
    force = "--force" in sys.argv
    dry_run = "--dry-run" in sys.argv

    print("=" * 60)
    print("Valoryx i18n Translation Sync")
    print("=" * 60)

    # 1. Parse English source
    en_file = I18N_DIR / f"{SOURCE_LANG}.toml"
    if not en_file.exists():
        print(f"ERROR: {en_file} not found")
        sys.exit(1)

    en_keys = parse_toml_keys(en_file)
    print(f"\nEnglish keys: {len(en_keys)}")

    # 2. Compute checksums and compare
    new_checksums = compute_checksums(en_keys)
    old_checksums = {} if force else load_checksums()

    # Find changed, new, and deleted keys
    changed = {}
    new = {}
    deleted = set(old_checksums.keys()) - set(new_checksums.keys())

    for key, checksum in new_checksums.items():
        if key in SKIP_KEYS:
            continue
        if key not in old_checksums:
            new[key] = en_keys[key]
        elif old_checksums[key] != checksum:
            changed[key] = en_keys[key]

    to_translate = {**changed, **new}

    print(f"Changed keys: {len(changed)}")
    print(f"New keys: {len(new)}")
    print(f"Deleted keys: {len(deleted)}")
    print(f"Keys to translate: {len(to_translate)}")

    if not to_translate and not deleted:
        print("\nAll translations are up to date.")
        save_checksums(new_checksums)
        return

    if to_translate:
        print("\nKeys to translate:")
        for k in sorted(to_translate.keys()):
            status = "NEW" if k in new else "CHANGED"
            print(f"  [{status}] {k}: {to_translate[k][:60]}...")

    if deleted:
        print("\nKeys to remove:")
        for k in sorted(deleted):
            print(f"  [DELETE] {k}")

    if dry_run:
        print("\n--dry-run: no files modified")
        return

    # 3. Translate
    api_key = get_api_key()
    if not api_key:
        print("\nWARNING: No OPENROUTER_API_KEY found. Using fallback (English with [EN] prefix).")
        print("Set OPENROUTER_API_KEY in environment or .env file for proper translation.")

    for lang in TARGET_LANGS:
        lang_file = I18N_DIR / f"{lang}.toml"
        lang_name = LANG_NAMES.get(lang, lang)

        if not lang_file.exists():
            print(f"\nWARNING: {lang_file} not found, skipping")
            continue

        print(f"\n{'─' * 40}")
        print(f"Translating to {lang_name} ({lang})")

        if to_translate:
            # Batch translate
            translations = {}
            keys_list = list(to_translate.items())

            for i in range(0, len(keys_list), BATCH_SIZE):
                batch = dict(keys_list[i:i + BATCH_SIZE])
                batch_num = i // BATCH_SIZE + 1
                total_batches = (len(keys_list) + BATCH_SIZE - 1) // BATCH_SIZE
                print(f"  Batch {batch_num}/{total_batches} ({len(batch)} keys)...", end=" ")

                if api_key:
                    result = translate_batch(batch, lang, api_key)
                    # Fill any missing keys with fallback
                    for k in batch:
                        if k not in result:
                            result[k] = f"[EN] {batch[k]}"
                else:
                    result = fallback_translate(batch)

                translations.update(result)
                print(f"OK ({len(result)} translated)")

            # Update TOML file
            update_toml_values(lang_file, translations, deleted)
            print(f"  Updated {lang_file.name}: {len(translations)} keys translated")
        elif deleted:
            # Only deletions
            update_toml_values(lang_file, {}, deleted)
            print(f"  Updated {lang_file.name}: {len(deleted)} keys removed")

    # 4. Save checksums
    save_checksums(new_checksums)
    print(f"\n{'=' * 60}")
    print(f"Checksums saved to {CHECKSUMS_FILE.name}")
    print(f"Total: {len(to_translate)} keys translated, {len(deleted)} keys deleted")
    print("Done.")


if __name__ == "__main__":
    main()
