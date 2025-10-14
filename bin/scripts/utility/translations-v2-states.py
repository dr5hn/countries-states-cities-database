import mysql.connector
import json
import os
from google.cloud import translate
from google.oauth2 import service_account
import time
import re
import sys
import datetime

PROJECT_ID = "deft-computing-473612-p3"

# Load Google Cloud credentials (env var first, then project default path)
CREDENTIALS_PATH = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "./bin/scripts/utility/gc-keys/cscdb-new-2.json",
)

try:
    _credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
    CLIENT = translate.TranslationServiceClient(credentials=_credentials)
    # Prefer project_id from credentials if present
    if getattr(_credentials, "project_id", None):
        PROJECT_ID = _credentials.project_id  # type: ignore
except Exception as e:
    print(f"Failed to load Google credentials from {CREDENTIALS_PATH}: {e}")
    CLIENT = translate.TranslationServiceClient()

languages = {
    "br": "Breton",
    "ko": "Korean",
    "pt-BR": "Portuguese (Brazil)",
    "pt": "Portuguese",
    "nl": "Dutch",
    "hr": "Croatian",
    "fa": "Persian",
    "de": "German",
    "es": "Spanish",
    "fr": "French",
    "ja": "Japanese",
    "it": "Italian",
    "zh-CN": "Chinese (Simplified)",
    "tr": "Turkish",
    "ru": "Russian",
    "uk": "Ukrainian",
    "pl": "Polish",
    "hi": "Hindi",
    "ar": "Arabic",
}

# Languages that should use transliteration instead of translation
# These preserve the original name but write it in the target script
TRANSLITERATE_LANGUAGES = {
    "ko", "hi", "zh-CN", "ar", "fa", "ja"
}

def translate_text_with_model(text, target_lang, project_id, source_lang="en", location="us-central1", max_retries=3, use_transliteration=False):
    parent = f"projects/{project_id}/locations/{location}"
    attempt = 0

    # Determine operation type for logging
    operation_type = "Transliterating" if use_transliteration else "Translating"

    while True:
        try:
            response = CLIENT.translate_text(
                request={
                    "contents": [text],
                    "target_language_code": target_lang,
                    "source_language_code": source_lang,
                    "parent": parent,
                    "mime_type": "text/plain",
                    "transliteration_config": { "enable_transliteration": use_transliteration}
                }
            )
            # Only print response in verbose mode to reduce clutter
            # print(response)
            for translation in response.translations:
                result = translation.transliterated_text if use_transliteration and hasattr(translation, 'transliterated_text') else translation.translated_text
                return result
        except Exception as e:
            message = str(e)

            # If transliteration is not supported, fall back to translation
            if use_transliteration and ("doesn't support" in message.lower() or "transliteration" in message.lower()):
                print(f"  ℹ️  Transliteration not supported for '{target_lang}', using translation instead")
                return translate_text_with_model(text, target_lang, project_id, source_lang, location, max_retries, use_transliteration=False)

            # Stop immediately on permission errors to avoid spamming the API
            if "permission" in message.lower() or "denied" in message.lower():
                print(f"  ⚠️  Permission error {operation_type.lower()} to '{target_lang}': {e}")
                return ""

            # For transliteration errors, don't retry - fail fast
            if use_transliteration:
                print(f"  ⚠️  {operation_type} failed for '{text}' to '{target_lang}': {e}")
                return ""

            # Retry on transient errors (only for translations)
            attempt += 1
            if attempt > max_retries:
                print(f"  ⚠️  {operation_type} failed for '{text}' to '{target_lang}' after {max_retries} retries: {e}")
                return ""
            backoff_seconds = min(2 ** attempt, 10)
            time.sleep(backoff_seconds)

def clean_translated_name(translated, original_name):
    """
    Remove 'State of' translations from the result to leave just the name.
    """
    translated = translated.strip()

    # Clean up pipes, punctuation, etc.
    translated = re.sub(r'[|,.;:\-–—]+$', '', translated).strip()

    # Lowercase copy for matching
    low = translated.lower()

    # Remove known "state" prefixes
    prefix_patterns = [
        r"^estado de ",        # Spanish, Portuguese
        r"^état d['']",         # French
        r"^state of ",          # English
        r"^staat ",             # German
        r"^staat van ",         # Dutch
        r"^dr[zž]ava ",         # Croatian
        r"^ایالت ",             # Persian
        r"^ولاية ",             # Arabic
        r"^uzak devlet",        # Turkish (bad translation)
        r"^государство ",       # Russian
        r"^штат ",              # Ukrainian
        r"^राज्य ",             # Hindi
        r"^शहर ",               # Hindi (city)
        r"^stato di ",          # Italian
        r"^stan ",              # Polish
        r"^stad ",              # Breton or Dutch
    ]

    for pattern in prefix_patterns:
        if re.match(pattern, low):
            translated = re.sub(pattern, '', translated, flags=re.IGNORECASE).strip()
            break

    # Remove known "state" suffixes
    suffix_patterns = [
        r" 주$",    # Korean "ju" (state/prefecture)
        r"州$",     # Japanese/Chinese
        r" राज्य$", # Hindi "Rajya"
        r" सरकार$", # Hindi "Sarkar" (gov/state)
    ]

    for pattern in suffix_patterns:
        if re.search(pattern, translated):
            translated = re.sub(pattern, '', translated, flags=re.IGNORECASE).strip()
            break

    return translated


def get_total_pending(conn):
    """Get total count of pending translations."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM states WHERE translations IS NULL OR translations = ''")
    total = cursor.fetchone()[0]
    cursor.close()
    return total


def main():
    # Parse command line arguments for batch number
    batch_number = 0
    if len(sys.argv) > 1:
        try:
            batch_number = int(sys.argv[1])
            if batch_number < 0:
                print("Batch number must be non-negative")
                sys.exit(1)
        except ValueError:
            print("Usage: python script.py [batch_number]")
            print("Example: python script.py 0  (processes records 0-4999)")
            print("Example: python script.py 1  (processes records 5000-9999)")
            sys.exit(1)

    BATCH_SIZE = 2700
    offset = batch_number * BATCH_SIZE

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='world')

    # Get total pending count
    total_pending = get_total_pending(conn)
    total_batches = (total_pending + BATCH_SIZE - 1) // BATCH_SIZE  # Ceiling division

    print(f"="*70)
    print(f"BATCH #{batch_number}")
    print(f"Total pending translations: {total_pending}")
    print(f"Total batches available: {total_batches}")
    print(f"Processing records {offset} to {offset + BATCH_SIZE - 1}")
    print(f"="*70)

    if offset >= total_pending:
        print(f"Batch {batch_number} is out of range. No records to process.")
        conn.close()
        return

    cursor = conn.cursor(dictionary=True)

    # Use LIMIT with OFFSET for batch processing
    query = """
        SELECT id, name
        FROM states
        WHERE translations IS NULL OR translations = ''
        LIMIT %s OFFSET %s
    """
    cursor.execute(query, (BATCH_SIZE, offset))
    states = cursor.fetchall()
    total = len(states)

    if total == 0:
        print(f"No records found for batch {batch_number}")
        cursor.close()
        conn.close()
        return

    print(f"Found {total} states to translate in this batch\n")
    counter = 0
    start_time = time.time()

    for state in states:
        counter += 1
        state_id = state['id']
        state_name = state['name']

        # Calculate progress percentage
        progress_pct = (counter / total) * 100

        print(f"\n{'─'*70}")
        print(f"[Batch {batch_number}] Progress: {counter}/{total} ({progress_pct:.1f}%)")
        print(f"State: {state_name} (ID: {state_id})")
        print(f"{'─'*70}")

        # Cache to avoid duplicate requests for normalized language codes for THIS state only
        normalized_cache = {}

        translations = {}

        for lang_code in languages:
            # Map 'pt-BR' to 'pt' for model if needed, and 'zh-CN' to 'zh'
            normalized_lang_code = lang_code.replace("pt-BR", "pt").replace("zh-CN", "zh")

            # Check if this language should use transliteration
            use_transliteration = lang_code in TRANSLITERATE_LANGUAGES
            operation = "🔤" if use_transliteration else "🌐"

            if normalized_lang_code in normalized_cache:
                translated = normalized_cache[normalized_lang_code]
                # Show cached result
                print(f"  {operation} {languages[lang_code]:20} → ✓ {translated} (cached)")
            else:
                print(f"  {operation} {languages[lang_code]:20} → ", end="", flush=True)
                translated = translate_text_with_model(
                    text=state_name,
                    target_lang=normalized_lang_code,
                    project_id=PROJECT_ID,
                    use_transliteration=use_transliteration
                )
                # Only clean if translation (not transliteration)
                if not use_transliteration:
                    translated = clean_translated_name(translated, state_name)
                normalized_cache[normalized_lang_code] = translated

                # Show result
                if translated:
                    print(f"✓ {translated}")
                else:
                    print(f"✗ Failed")

            translations[lang_code] = translated if translated else ""

        translations_json = json.dumps(translations, ensure_ascii=False)
        cursor.execute("UPDATE states SET translations = %s WHERE id = %s", (translations_json, state_id))

        # Commit after each state to avoid losing progress
        conn.commit()
        print(f"  💾 Saved to database")

        # Calculate estimated time remaining
        if counter % 10 == 0:
            elapsed = time.time() - start_time
            avg_time_per_state = elapsed / counter
            remaining_states = total - counter
            eta_seconds = avg_time_per_state * remaining_states
            eta = str(datetime.timedelta(seconds=int(eta_seconds)))
            print(f"\n  ⏱️  Average: {avg_time_per_state:.1f}s per state | ETA: {eta}")

    print(f"\n{'='*70}")
    print(f"Batch {batch_number} complete! Processed {total} states.")
    elapsed_total = time.time() - start_time
    print(f"Total time: {str(datetime.timedelta(seconds=int(elapsed_total)))}")
    print(f"{'='*70}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
