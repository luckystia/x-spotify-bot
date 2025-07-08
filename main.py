import os
import spotipy
import tweepy
import datetime
import requests
import base64

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REFRESH_TOKEN = os.getenv("SPOTIPY_REFRESH_TOKEN")

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

LAST_TRACK_FILE = "last_track.txt"

def get_last_track_id():
    try:
        with open(LAST_TRACK_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_track_id(track_id):
    with open(LAST_TRACK_FILE, 'w') as f:
        f.write(str(track_id))

def get_new_access_token():
    auth_string = f"{SPOTIPY_CLIENT_ID}:{SPOTIPY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": SPOTIPY_REFRESH_TOKEN
    }
    
    result = requests.post(url, headers=headers, data=data)
    result.raise_for_status()
    json_result = result.json()
    new_access_token = json_result.get("access_token")
    
    if not new_access_token:
        raise Exception("Gagal mendapatkan access_token dari respons Spotify.")
    return new_access_token

print("Script dimulai...")
try:
    access_token = get_new_access_token()
    sp = spotipy.Spotify(auth=access_token)
    print("Otentikasi Spotify berhasil.")
    
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    twitter_api = tweepy.API(auth)
    print("Otentikasi Twitter berhasil.")

    current = sp.current_playback()
    if current and current.get('is_playing') and current.get('item'):
        current_track_id = current['item']['id']
        last_track_id = get_last_track_id()

        if current_track_id != last_track_id:
            song = current['item']['name']
            artist = current['item']['artists'][0]['name']
            link = current['item']['external_urls']['spotify']
            time_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%I:%M %p · %d %B %Y")
            tweet_text = f"Hi! Lukis now listening to {song}, played by {artist}.\n\nAs of {time_now} (WIB)\n{link}"
            twitter_api.update_status(tweet_text)
            save_last_track_id(current_track_id)
            print(f"Tweet terkirim: {song}")
        else:
            print("Lagu masih sama, tidak ada tweet baru.")
    else:
        print("Spotify tidak sedang memutar lagu.")
except Exception as e:
    print(f"Terjadi error: {e}")
    exit(1)
print("Script selesai.")
