import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def read_spotify_credentials(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    client_id = config['spotify']['client_id']
    client_secret = config['spotify']['client_secret']
    return client_id, client_secret


client_id, client_secret = read_spotify_credentials('./spotipy_info.ini')

auth_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)


def search_and_confirm_song(sp, track_name):
    result = sp.search(q=track_name, type='track', limit=1)
    if result['tracks']['items']:
        track = result['tracks']['items'][0]
        track_id = track['id']
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        print(f"Found: {track_name} by {artist_name}")
        confirm = input("Is this the correct song? (yes/no): ").strip().lower()
        if confirm == 'yes':
            return track_id
    print(f"Could not find or confirm track: {track_name}")
    return None


def get_playlists_with_tracks(sp, track_ids):
    playlists = []
    query = ' '.join([f'track:{track_id}' for track_id in track_ids])
    results = sp.search(q=query, type='playlist', limit=50)

    for playlist in results['playlists']['items']:
        playlist_id = playlist['id']
        playlist_tracks = sp.playlist_tracks(playlist_id)
        playlist_track_ids = [item['track']['id']
                              for item in playlist_tracks['items']]

        if all(track_id in playlist_track_ids for track_id in track_ids):
            playlists.append(playlist)

    return playlists


def main():
    # Prompt user for three song titles and confirm each one
    track_ids = []
    for i in range(3):
        while True:
            track_name = input(f"Enter the title of song {i + 1}: ")
            track_id = search_and_confirm_song(sp, track_name)
            if track_id:
                track_ids.append(track_id)
                break

    # Find playlists containing all tracks
    playlists = get_playlists_with_tracks(sp, track_ids)

    # Print the results
    if playlists:
        print("Playlists containing all three songs:")
        for playlist in playlists:
            print(f"{playlist['name']}: \
                  {playlist['external_urls']['spotify']}")
    else:
        print("No playlists found containing all three songs.")


if __name__ == "__main__":
    main()
