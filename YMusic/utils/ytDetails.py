from youtubesearchpython import VideosSearch, PlaylistsSearch
from urllib.parse import urlparse, parse_qs
from pytube import YouTube
import yt_dlp
import config

async def searchYt(query):
    try:
        videosSearch = VideosSearch(query, limit=1)
        result = videosSearch.result()
        if not result["result"]:
            return None, None, None
        title = result["result"][0]["title"]
        duration = result["result"][0]["duration"]
        link = result["result"][0]["link"]
        return title, duration, link
    except Exception as e:
        print(f"Error in searchYt: {e}")
        return None, None, None

async def download_audio(link, file_name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{file_name}.%(ext)s',
        'cookiefile': config.COOK_PATH,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        return f"{file_name}.mp3"
    except yt_dlp.utils.DownloadError as e:
        print(f"Download error: {e}")
        return None
    except yt_dlp.utils.ExtractorError as e:
        print(f"Extractor error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in download_audio: {e}")
        return None

def searchPlaylist(query):
    query = str(query)
    playlistResult = PlaylistsSearch(query, limit=1)
    Result = playlistResult.result()
    if not Result["result"] == []:
        title = Result["result"][0]["title"]
        videoCount = Result["result"][0]["videoCount"]
        link = Result["result"][0]["link"]
        return title, videoCount, link
    return None, None, None


def extract_playlist_id(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    playlist_id = query_params.get('list', [None])[0]
    return playlist_id


def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        video_id = parsed_url.path[1:]
    else:
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get('v', [None])[0]
    return video_id
