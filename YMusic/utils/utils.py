import os
import glob
import re
import asyncio
import aiohttp
import json
from urllib.parse import quote

from YMusic import app
from YMusic.utils.formaters import format_time
# Impor fungsi lain yang diperlukan

MAX_MESSAGE_LENGTH = 4096

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

async def get_lyrics(query):
    encoded_query = quote(query)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://api.safone.dev/lyrics?title={encoded_query}") as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return None
        except Exception as e:
            print(f"Error fetching lyrics: {e}")
            return None

async def send_song_info(chat_id, song, is_loop=False):
    original_query = song.get('query', song['title'])
    processed_query = extract_song_title(original_query)
    title = song['title']
    duration = song['duration']
    link = song['link']
    requester_name = song['requester_name']
    requester_id = song['requester_id']

    lyrics_data = await get_lyrics(processed_query)
    
    # Informasi lagu
    info_text = f"🎵 {'Memutar ulang' if is_loop else 'Sedang diputar'}:\n\n"
    info_text += f"Judul: [{title}]({link})\n"
    info_text += f"Durasi: {format_time(duration)}\n"
    info_text += f"Direquest oleh: [{requester_name}](tg://user?id={requester_id})\n"

    # Kirim informasi lagu
    await app.send_message(chat_id, info_text, disable_web_page_preview=True)

    # Jika lirik ditemukan, kirim sebagai pesan terpisah
    if lyrics_data:
        lyrics = lyrics_data['lyrics']
        lyrics_text = f"📜 Lirik:\n\n{lyrics}"
        
        if len(lyrics_text) <= MAX_MESSAGE_LENGTH:
            await app.send_message(chat_id, lyrics_text)
        else:
            # Jika lirik terlalu panjang, bagi menjadi beberapa pesan
            chunks = [lyrics_text[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(lyrics_text), MAX_MESSAGE_LENGTH)]
            for chunk in chunks:
                await app.send_message(chat_id, chunk)
    else:
        await app.send_message(chat_id, "Lirik tidak ditemukan.")
