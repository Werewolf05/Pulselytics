import os
import re
from datetime import datetime
import pandas as pd

# Data directory is one level up from scripts/
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

COLUMNS = [
    "platform", "username", "post_url", "caption", "media_url",
    "likes", "comments", "views", "upload_date"
]

def now_iso() -> str:
    return datetime.utcnow().isoformat()


def save_csv(df: pd.DataFrame, filename: str) -> str:
    """Save or merge a DataFrame into a CSV under data/.

    If the file already exists, merge by concatenating and de-duplicating on
    the unique post URL so we accumulate data across multiple scrapes/clients
    instead of overwriting.
    """
    # Ensure standard columns exist and order
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[COLUMNS]

    path = os.path.join(DATA_DIR, filename)

    try:
        if os.path.exists(path):
            existing = pd.read_csv(path)
            # Align columns
            for col in COLUMNS:
                if col not in existing.columns:
                    existing[col] = None
            existing = existing[COLUMNS]
            combined = pd.concat([existing, df], ignore_index=True)
            # Drop duplicates based on post_url (unique per post)
            if 'post_url' in combined.columns:
                combined = combined.drop_duplicates(subset=['post_url'], keep='last')
            # Optional: sort by upload_date desc if present
            if 'upload_date' in combined.columns:
                combined['upload_date'] = pd.to_datetime(combined['upload_date'], errors='coerce')
                combined = combined.sort_values('upload_date', ascending=False)
            df_to_save = combined
        else:
            df_to_save = df
    except Exception:
        # Fallback to just saving the new df if anything goes wrong during merge
        df_to_save = df

    df_to_save = df_to_save[COLUMNS]
    df_to_save.to_csv(path, index=False, encoding='utf-8')
    return path
