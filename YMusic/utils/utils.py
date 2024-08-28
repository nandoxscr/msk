import os
import glob
import re

def extract_song_title(query):
    # Pola untuk mencocokkan format umum judul lagu
    patterns = [
        r'^(.*?)\s*(\(cover\)|\(feat\..*?\)|\(ft\..*?\)|\bcover\b|\bfeat\.|\bft\.).*$',
        r'^(.*?)\s*-\s*.*$',
        r'^(.*?)\s*by\s*.*$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Jika tidak ada pola yang cocok, kembalikan dua kata pertama dari query
    words = query.split()
    return ' '.join(words[:min(3, len(words))])

def clear_downloads_cache():
    downloads_path = os.path.join(os.getcwd(), "downloads")
    files = glob.glob(os.path.join(downloads_path, "*"))
    for f in files:
        try:
            os.remove(f)
            print(f"Removed file: {f}")
        except Exception as e:
            print(f"Error removing {f}: {e}")
            
async def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File deleted successfully: {file_path}")
        else:
            print(f"File does not exist: {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
