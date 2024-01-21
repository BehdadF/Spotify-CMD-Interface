from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError
import json
import pprint
import sys

class SpotifyManager:
    def __init__(self, client_id, client_secret, 
                 username,
                 scope="playlist-modify-private" 
                        "playlist-read-private" 
                        "user-library-read", 
                 redirect_uri="https://example.com/") -> None:
        """
        Initialize the SpotifyManager instance.

        Parameters:
            client_id (str): Spotify API client ID.
            client_secret (str): Spotify API client secret.
            username (str): Spotify username.
            scope (str): Spotify API scope.
            redirect_uri (str): Redirect URI for Spotify authentication.
        """
        self.user = ""
        self.user_id = ""
        self.username = username
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = ""
        self.scope = scope
        
        self.redirect_uri = redirect_uri
        self.cache_path = "./token.txt"

        self.authenticate()
        self.set_user_id()

    def access_token(self):
        """
        Read and set the access token from the token cache file.
        """
        try:
            with open(self.cache_path, 'r') as file:
                data = file.read()
                data = json.loads(data)
                if data['access_token']:
                    self.token = data['access_token']
        except FileNotFoundError:
            pass

    def authenticate(self) -> Spotify:
        """
        Authenticate with the Spotify API using OAuth.

        Returns:
            Spotify: Spotify API client.
        """
        try:
            self.user = Spotify(auth_manager=SpotifyOAuth(client_id=self.client_id, 
                                                    client_secret=self.client_secret,
                                                    redirect_uri=self.redirect_uri, 
                                                    scope=self.scope,
                                                    cache_path= self.cache_path
                                                    ))
        except SpotifyOauthError as e:
            print(f"Something went wrong with your authentication: {e}")
            sys.exit(1)

    def set_user_id(self) -> None:
        """
        Set the Spotify user ID for the current user.
        """
        self.user_id = self.user.current_user()['id']

    def playlist_exists(self, wanted_playlist) -> bool:
        """
        Check if a playlist with the given name exists for the current user.

        Parameters:
            wanted_playlist (str): Name of the playlist to check.

        Returns:
            bool: True if the playlist exists, False otherwise.
        """
        playlists = self.user.user_playlists(self.username)
        for playlist in playlists['items']:
            if wanted_playlist == playlist["name"]:
                return True
        return False

    def create_private_playlist(self, playlist_name) -> bool:
        """
        Create a private playlist for the current user.

        Parameters:
            playlist_name (str): Name of the playlist to create.

        Returns:
            bool: True if the playlist was created successfully, False otherwise.
        """
        self.user.user_playlist_create(self.user_id, playlist_name, public=False)

    def track_exists(self, playlist_name, track_name) -> bool:
        """
        Check if a track with the given name exists in a playlist.

        Parameters:
            playlist_name (str): Name of the playlist to check.
            track_name (str): Name of the track to check.

        Returns:
            bool: True if the track exists, False otherwise.
        """
        pID = self.get_playlist_id(playlist_name)
        tracks = self.user.playlist_tracks(pID)
        track_names = {track['track']['name'] for track in tracks["items"]}
        return track_name in track_names


    
    def get_track_uri(self, playlist_name, track_name):
        """
        Get the URI of a track in a specified playlist.

        Parameters:
            playlist_name (str): Name of the playlist.
            track_name (str): Name of the track.

        Returns:
            str: URI of the track if it exists, otherwise None.
        """
        try:
            if self.track_exists(playlist_name, track_name):
                pID = self.get_playlist_id(playlist_name)
                tracks = self.user.playlist_tracks(pID)
                for track in tracks["items"]:
                    if track_name == track['track']['name']:
                        return track['track']['uri']
            else:
                print("The track does not exist")
        except:
            print("Something went wrong!")

    def add_track(self, playlist_name, track_name, **kwargs) -> None:
        """
        Add a track to the specified playlist.

        Parameters:
            playlist_name (str): Name of the playlist.
            track_name (str): Name of the track.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        try:
            if not self.track_exists(playlist_name, track_name):
                playlist_id = self.get_playlist_id(playlist_name)
                uri_list = self.get_uris("track" ,track_name, **kwargs)
                self.user.playlist_add_items(playlist_id=playlist_id, items=[uri_list])
                print('[Completed.]\n[1] track was successfully added.')
        except:
            print(f"No such track exists")

    def add_album(self, playlist_name, album_name, **kwargs) -> None:
        """
        Add all tracks from an album to the specified playlist.

        Parameters:
            playlist_name (str): Name of the playlist.
            album_name (str): Name of the album.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        track_count = 0
        added_tracks = []
        try:
            playlist_id = self.get_playlist_id(playlist_name)
            result = self.search("album", album_name, **kwargs)
            album_id = result["albums"]["items"][0]["id"]
            res = self.user.album_tracks(album_id)
            for track in res['items']:
                if not self.track_exists(playlist_name, track['name']):
                    track_count += 1
                    added_tracks.append(track['name'])
                # self.add_track(playlist_id, track['name'])
                    self.user.playlist_add_items(playlist_id, items=[track['uri']])
            print(f'[Completed.]\n[{track_count}] track was successfully added.')
            print("\nList of the deleted tracks: ")
            print("============================")
            pprint.pprint(added_tracks)
            print("============================")
        except:
            print("No such album exists")
           
    def get_playlist_info(self, playlist_name, type):
        """
        Get information (ID or URI) about a playlist.

        Parameters:
            playlist_name (str): Name of the playlist.
            type (str): Type of information to retrieve (id, uri).

        Returns:
            str: ID or URI of the playlist.
        """
        result = self.user.user_playlists(self.username)
        for item in result['items']:
            if playlist_name == item['name']:
                return item[type]
    # def get_playlist_uri(self, playlist_name):
        # result = self.user.user_playlists(self.username)
        # for item in result['items']:
        #     if playlist_name == item['name']:
        #         return item['uri']

    # For publics
    def get_public_uris(self, type, name, **kwargs):
        """
        Get the URI of a public resource (track, album, etc.).

        Parameters:
            type (str): Type of the resource (track, album, etc.).
            name (str): Name of the resource.
            **kwargs: Additional keyword arguments.

        Returns:
            str: URI of the resource.
        """
        result = self.search(f"{type}", name, **kwargs)
        uri = result[f"{type}s"]["items"][0]["uri"]
        return uri
    
    def search(self, type, name, **kwargs):
        """
        Search for a resource (track, album, etc.) on Spotify.

        Parameters:
            type (str): Type of the resource (track, album, etc.).
            name (str): Name of the resource.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: Spotify search result.
        """
        query = f"{type}:{name}"
        for key, value in kwargs.items():
            query += f" {key}:{value}"
        return self.user.search(q=query, type=type)

    def delete_track(self, track_name, playlist_name):
        """
        Delete a track from a playlist.

        Parameters:
            track_name (str): Name of the track.
            playlist_name (str): Name of the playlist.

        Returns:
            None
        """
        playlist_uri = self.get_playlist_info(playlist_name, 'uri')
        track_uri = self.get_track_uri(playlist_name, track_name)
        self.user.playlist_remove_all_occurrences_of_items(playlist_uri, [track_uri])
        # print(f'[Completed.]\n1 track was successfully deleted.')

    def delete_album(self, album_name, playlist_name):
        """
        Delete all tracks from a specified album in a playlist.

        Parameters:
            album_name (str): Name of the album.
            playlist_name (str): Name of the playlist.

        Returns:
            None
        """
        # counter = 0
        deleted_items = []
        # playlist_uri = self.get_playlist_info(playlist_name, 'uri')
        album_uri = self.get_public_uris('album', album_name)
        tracks = self.user.album(album_uri)
        for counter, item in enumerate(tracks['tracks']['items']):
            # counter += 1
            if not self.track_exists(playlist_name, item['name']):
                deleted_items.append(item['name'])
                self.delete_track(item['name'], playlist_name)
                # item_uri = item['uri']
                # self.user.playlist_remove_all_occurrences_of_items(playlist_uri, [item_uri])
        print(f'[Completed.]\n{counter+1} tracks was successfully deleted.')
        print("\nList of the deleted tracks: ")
        print("============================")
        pprint.pprint(deleted_items)
        print("============================")

    def print_playlists(self):
        """
        Print the names of the user's private playlists.

        Returns:
            None
        """
        result = self.user.user_playlists(self.username)
        # counter = 0
        print("\nCurrent Private Playlists:")
        print("========================")
        for counter, item in enumerate(result['items']):
            # counter += 1
            print(f"{counter+1}: {item['name']}")
        print("========================")

    def print_tracklist(self, playlist):
        """
        Print the names of tracks in a specified playlist.

        Parameters:
            playlist (str): Name of the playlist.

        Returns:
            None
        """
        pID = self.get_playlist_id(playlist)
        tracks = self.user.playlist_tracks(pID)
        print(f"\nTracks in {playlist}")
        print("========================")
        # counter = 0
        for counter, track in enumerate(tracks["items"]):
            # counter += 1
            print(f"{counter+1}: {track['track']['name']}")
        print("========================")
