import requests
import json
import os
import re
import time
import shutil
import sys
from datetime import datetime

# ── CONFIG ───────────────────────────────────────────────────────────────────
# Step 1: Go to https://leetcode.com and log in
# Step 2: Press F12 → Application → Cookies → https://leetcode.com
# Step 3: Copy the values of LEETCODE_SESSION and csrftoken and paste below

LEETCODE_SESSION = "YOUR_LEETCODE_SESSION_COOKIE"
CSRF_TOKEN       = "YOUR_CSRF_TOKEN_COOKIE"

# Full path to the folder where your Java files should be saved
DEST_FOLDER = r"C:\Users\YourName\path\to\your\Java programs"

# ─────────────────────────────────────────────────────────────────────────────

LOG_FILE    = os.path.join(DEST_FOLDER, "sync_log.txt")
SYNCED_FILE = os.path.join(DEST_FOLDER, ".synced_ids.json")

# Folders that will never be deleted during a reset
PROTECTED_FOLDERS = {".vscode", ".git", ".idea", "node_modules"}

GRAPHQL_URL = "https://leetcode.com/graphql"
topic_cache = {}


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(DEST_FOLDER, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_session():
    """Create an authenticated requests session using browser cookies."""
    session = requests.Session()
    session.cookies.set("LEETCODE_SESSION", LEETCODE_SESSION, domain="leetcode.com")
    session.cookies.set("csrftoken", CSRF_TOKEN, domain="leetcode.com")
    session.headers.update({
        "Referer": "https://leetcode.com/",
        "Origin": "https://leetcode.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "x-csrftoken": CSRF_TOKEN,
    })
    return session


def load_synced_ids():
    """Load the set of already-synced submission IDs from disk."""
    if os.path.exists(SYNCED_FILE):
        with open(SYNCED_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_synced_ids(ids: set):
    """Save the set of synced submission IDs to disk."""
    with open(SYNCED_FILE, "w") as f:
        json.dump(list(ids), f)


def to_filename(title):
    """Convert a problem title to a PascalCase .java filename."""
    words = re.sub(r"[^a-zA-Z0-9 ]", "", title).split()
    return "".join(w.capitalize() for w in words) + ".java"


def get_primary_topic(session, title_slug):
    """Fetch the first topic tag for a problem via LeetCode's GraphQL API."""
    if title_slug in topic_cache:
        return topic_cache[title_slug]

    query = """
    query problemTopics($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        topicTags {
          name
        }
      }
    }
    """
    try:
        resp = session.post(
            GRAPHQL_URL,
            json={"query": query, "variables": {"titleSlug": title_slug}},
            headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
        data = resp.json()
        tags = data.get("data", {}).get("question", {}).get("topicTags", [])
        topic = tags[0]["name"] if tags else "Uncategorized"
    except Exception:
        topic = "Uncategorized"

    topic_cache[title_slug] = topic
    return topic


def reset_folder():
    """Delete all synced .java files and topic subfolders to start fresh."""
    print("\nResetting your Java programs folder...")

    if os.path.exists(SYNCED_FILE):
        os.remove(SYNCED_FILE)
        print("  Deleted: .synced_ids.json")

    deleted_files = deleted_folders = skipped_folders = 0

    for item in os.listdir(DEST_FOLDER):
        item_path = os.path.join(DEST_FOLDER, item)

        if os.path.isfile(item_path) and item.endswith(".java"):
            os.remove(item_path)
            deleted_files += 1

        elif os.path.isdir(item_path):
            if item in PROTECTED_FOLDERS:
                print(f"  Skipped protected folder: {item}")
                skipped_folders += 1
                continue
            try:
                shutil.rmtree(item_path)
                deleted_folders += 1
            except PermissionError:
                print(f"  Skipped (no permission): {item}")
                skipped_folders += 1

    print(f"  Deleted: {deleted_files} .java file(s), {deleted_folders} topic folder(s)")
    if skipped_folders:
        print(f"  Skipped: {skipped_folders} protected/system folder(s)")
    print("Reset done! Starting fresh sync...\n")


def sync(do_reset=False):
    if LEETCODE_SESSION == "YOUR_LEETCODE_SESSION_COOKIE" or CSRF_TOKEN == "YOUR_CSRF_TOKEN_COOKIE":
        print("ERROR: Please open the script and fill in your LEETCODE_SESSION and CSRF_TOKEN!")
        print("See the README for instructions on how to get these values.")
        return

    os.makedirs(DEST_FOLDER, exist_ok=True)

    if do_reset:
        print("=" * 50)
        print("       LeetCode Java Sync Tool")
        print("=" * 50)
        choice = input("\nReset and re-sync everything from scratch? (y/n): ").strip().lower()
        if choice == "y":
            reset_folder()
        else:
            print("Skipping reset. Doing incremental sync instead.\n")
    else:
        log("Running scheduled incremental sync...")

    synced_ids = load_synced_ids()
    new_count  = 0
    offset     = 0
    limit      = 20

    log("=== LeetCode Sync Started ===")
    session = get_session()

    while True:
        url = f"https://leetcode.com/api/submissions/?offset={offset}&limit={limit}"
        try:
            resp = session.get(url)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            log(f"ERROR fetching submissions: {e}")
            break

        submissions = data.get("submissions_dump", [])
        if not submissions:
            break

        for sub in submissions:
            if sub.get("lang", "").lower() != "java":
                continue
            if sub.get("status") != 10:  # 10 = Accepted
                continue

            sub_id = str(sub["id"])
            if sub_id in synced_ids:
                continue

            title      = sub["title"]
            title_slug = sub.get("title_slug") or re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            code       = sub.get("code", "")

            if not code:
                continue

            # Fetch the primary topic tag → use as subfolder name
            time.sleep(0.5)
            topic        = get_primary_topic(session, title_slug)
            safe_topic   = re.sub(r'[\\/*?:"<>|]', "", topic).strip()
            topic_folder = os.path.join(DEST_FOLDER, safe_topic)
            os.makedirs(topic_folder, exist_ok=True)

            filename = to_filename(title)
            filepath = os.path.join(topic_folder, filename)

            header = (
                f"// LeetCode - {title}\n"
                f"// Topic   : {topic}\n"
                f"// Synced  : {datetime.now().strftime('%Y-%m-%d')}\n\n"
            )

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(header + code)

            synced_ids.add(sub_id)
            new_count += 1
            log(f"Saved: [{safe_topic}] {filename}")

        if not data.get("has_next", False):
            break

        offset += limit
        time.sleep(1)

    save_synced_ids(synced_ids)
    log(f"=== Sync Complete. {new_count} new file(s) saved. ===\n")


if __name__ == "__main__":
    # Usage:
    #   python leetcode_sync.py           → silent incremental sync (for Task Scheduler)
    #   python leetcode_sync.py --reset   → interactive reset + full re-sync
    do_reset = "--reset" in sys.argv
    sync(do_reset=do_reset)