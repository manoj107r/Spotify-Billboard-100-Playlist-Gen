from bs4 import BeautifulSoup
import requests
import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth

Client_ID = "YOUR ID"
Client_Secret = "YOUR CLIENT SECRET CODE"


def ask_date():
    # Ask user for the date to time travel back to until it gets proper input.
    date = input('Which date do you want to travel to? [Format YYYY-MM-DD]:\n')

    # Date input validation
    date_format = '%Y-%m-%d'  # YYYY-MM-DD
    try:
        datetime.datetime.strptime(date, date_format)
        return date
    except ValueError:
        print('Incorrect date format. Should be YYYY-MM-DD')
        ask_date()


def get_top100Songs(beautifulSoup_object: BeautifulSoup):
    # Get a list of top 100 songs
    class_name1 = "c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 u-max-width-230@tablet-only u-letter-spacing-0028@tablet"
    class_name2_100 = 'c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only'
    songs_h3_tags = soup.findAll(
        'h3', attrs={'class': [class_name1, class_name2_100]})
    top100songs = [song.getText().strip() for song in songs_h3_tags]
    return top100songs


date = ask_date()
request_url = f"https://www.billboard.com/charts/hot-100/{date}"
response = requests.get(request_url)
soup = BeautifulSoup(response.text, 'html.parser')
top_100_songs = get_top100Songs(soup)

# Spotify Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=Client_ID,
        client_secret=Client_Secret,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]

song_uris = []
year = date.split("-")[0]
song_count = 0
rank_no = 0
for song in top_100_songs:
    result = sp.search(q=f"track:{song}", type="track")
    rank_no += 1
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
        print(
            f'Rank No{rank_no}. {result["tracks"]["items"][0]["name"]} found.')
        song_count += 1
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")
print(f"{song_count} songs found out of 100.")

# Creating a new private playlist in Spotify
playlist = sp.user_playlist_create(
    user=user_id, name=f"{date} Billboard 100", public=False)
print(f"{playlist['name']} created.")

# Add the song URI's into the new playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
