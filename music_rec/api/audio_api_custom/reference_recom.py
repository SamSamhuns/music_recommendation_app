import dotenv
import spotipy
import pandas as pd


dotenv.load_dotenv()


def get_playlist_data(playlist_id):
    # Set up Spotipy with the access token
    sp = spotipy.Spotify(
        auth_manager=spotipy.oauth2.SpotifyOAuth(
            redirect_uri="http://127.0.0.1:8888/callback",
            scope="user-library-read playlist-read-private",
        )
    )
    # Get the tracks from the playlist
    playlist_tracks = sp.playlist_tracks(
        playlist_id, fields="items(track(id, name, artists, album(id, name)))"
    )

    # Extract relevant information and store in a list of dictionaries
    music_data = []
    for track_info in playlist_tracks["items"]:
        track = track_info["track"]
        track_name = track["name"]
        artists = ", ".join([artist["name"] for artist in track["artists"]])
        album_name = track["album"]["name"]
        album_id = track["album"]["id"]
        track_id = track["id"]

        try:
            # Get audio features for the track
            # audio_features = sp.audio_features(track_id)[0] if track_id else None

            # Get release date of the album
            album_info = sp.album(album_id) if album_id else None
            release_date = album_info["release_date"] if album_info else None

            # Get popularity of the track
            track_info = sp.track(track_id) if track_id else None
            popularity = track_info["popularity"] if track_info else None

            # Add additional track information to the track data
            track_data = {
                "Track Name": track_name,
                "Artists": artists,
                "Album Name": album_name,
                "Album ID": album_id,
                "Track ID": track_id,
                "Popularity": popularity,
                "Release Date": release_date,
                "Explicit": track_info.get("explicit", None),
                "External URLs": track_info.get("external_urls", {}).get("spotify", None),
                # "Duration(ms)": audio_features["duration_ms"] if audio_features else None,
                # "Danceability": audio_features["danceability"] if audio_features else None,
                # "Energy": audio_features["energy"] if audio_features else None,
                # "Key": audio_features["key"] if audio_features else None,
                # "Loudness": audio_features["loudness"] if audio_features else None,
                # "Mode": audio_features["mode"] if audio_features else None,
                # "Speechiness": audio_features["speechiness"] if audio_features else None,
                # "Acousticness": audio_features["acousticness"] if audio_features else None,
                # "Instrumentalness": audio_features["instrumentalness"] if audio_features else None,
                # "Liveness": audio_features["liveness"] if audio_features else None,
                # "Valence": audio_features["valence"] if audio_features else None,
                # "Tempo": audio_features["tempo"] if audio_features else None,
                # Add more attributes as needed
            }

            music_data.append(track_data)
        except Exception as e:
            print(f"Error processing track {track_name}: {str(e)}")

    # Create a pandas DataFrame from the list of dictionaries
    df = pd.DataFrame(music_data)

    return df


PLAYLIST_ID = "36v68OiLl6Qlo9PEconeHk"
music_df = get_playlist_data(PLAYLIST_ID)

print(music_df)
print(music_df.isnull().sum())
