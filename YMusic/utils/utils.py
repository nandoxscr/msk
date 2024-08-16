import os
import glob

def clear_downloads_cache():
    downloads_path = os.path.join(os.getcwd(), "downloads")
    files = glob.glob(os.path.join(downloads_path, "*"))
    for f in files:
        try:
            os.remove(f)
            print(f"Removed file: {f}")
        except Exception as e:
            print(f"Error removing {f}: {e}")