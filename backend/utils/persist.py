import os
import shutil
import time
import threading
from huggingface_hub import HfApi, hf_hub_download, upload_file

DB_FILE = os.environ.get("DB_FILE", "checkin.db")
REPO_ID = os.environ.get("SPACE_ID", "wu549337178/check-in-system")
SAVE_INTERVAL = int(os.environ.get("DB_SAVE_INTERVAL", "300"))


def get_db_path():
    data_dir = "/data" if os.path.isdir("/data") else "."
    return os.path.join(data_dir, DB_FILE)


def restore_database():
    db_path = get_db_path()
    try:
        hf_hub_download(
            repo_id=REPO_ID,
            filename=DB_FILE,
            repo_type="space",
            local_dir=os.path.dirname(db_path),
            token=os.environ.get("HF_TOKEN"),
        )
        print(f"[persist] database restored from {REPO_ID}")
    except Exception:
        print(f"[persist] no remote database found, using local")


def save_database():
    db_path = get_db_path()
    if not os.path.isfile(db_path):
        return
    try:
        upload_file(
            path_or_fileobj=db_path,
            path_in_repo=DB_FILE,
            repo_id=REPO_ID,
            repo_type="space",
            token=os.environ.get("HF_TOKEN"),
        )
        print(f"[persist] database saved to {REPO_ID}")
    except Exception as e:
        print(f"[persist] save failed: {e}")


def start_persist_loop():
    def loop():
        while True:
            time.sleep(SAVE_INTERVAL)
            save_database()

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    print(f"[persist] auto-save every {SAVE_INTERVAL}s")
