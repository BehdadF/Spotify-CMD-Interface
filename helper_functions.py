import argparse
from spotifyManager import SpotifyManager
import sys

# ============================
# # URLs
REDIRECT_URL = "https://example.com/"

# Confidentialities
CLIENT_ID = ""
CLIENT_SECRET = ""
USERNAME = ""
# SCOPE
SCOPE = "playlist-modify-private playlist-modify-public playlist-read-private user-library-read"
# ============================

def playlist_checker(spotify, p):
    """
    Check if a playlist exists and prompt the user to create a new one if it doesn't.

    Parameters:
        p (str): Name of the playlist.
    """
    if not spotify.playlist_exists(p):
        if input("The playlist does not exist, \
                 Do you wanna create a new one? (Yes/No): ").strip().lower() == 'yes':
            spotify.create_private_playlist(p)

# Terminal Arguments
def get_args():
    """
    Define and parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    nparser = argparse.ArgumentParser(description='manage spotify')
    subparsers = nparser.add_subparsers(dest='commands', title='command', description='')

    add_track_parser = subparsers.add_parser('add_track', help='add a track to your spotify')
    add_track_parser.add_argument('-p', '--playlist', required=True, help='Name of the playlist')
    add_track_parser.add_argument('-t', '--track', required=True, help='Name of the track')
    add_track_parser.add_argument('-a', '--artist', required=False, help='Name of the artist')

    add_album_parser = subparsers.add_parser('add_album', help='add an album to your spotify')
    add_album_parser.add_argument('-p', '--playlist', required=True, help='Name of the playlist')
    add_album_parser.add_argument('-b', '--album', required=True, help='Name of the album')
    add_album_parser.add_argument('-a', '--artist', required=False, help='Name of the artist')

    print_parser = subparsers.add_parser('print', help='print')
    group = print_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--playlist', action="store_true", help='print private playlists')
    group.add_argument('-t', '--track', type=str, help='print track information with a specified playlist')
    
    delete_track_parser = subparsers.add_parser('delete_track', help='delete a track from spotify')
    delete_track_parser.add_argument('-t', '--track', type=str, required=True, help='specify the track name you wanna delete.')
    delete_track_parser.add_argument('-p', '--playlist', type=str, required=True, help='specify the playlist name')

    delete_album_parser = subparsers.add_parser('delete_album', help='delete a album from spotify')
    delete_album_parser.add_argument('-a', '--album', type=str, required=True, help='specify the album name you wanna delete.')
    delete_album_parser.add_argument('-p', '--playlist', type=str, required=True, help='specify the playlist name')   



    if len(sys.argv) == 1:
        nparser.print_help()
    return nparser


def main():

    parser = get_args()
    args = parser.parse_args()


    spotify = SpotifyManager(CLIENT_ID, CLIENT_SECRET, USERNAME, SCOPE, REDIRECT_URL)

    if args.commands == 'add_track':
        playlist_checker(spotify, args.playlist)
        spotify.add_track(args.playlist, track_name=args.track, 
                        artist=args.artist if args.artist else None)

    elif args.commands == 'add_album':
        playlist_checker(args.playlist) 
        spotify.add_album(args.playlist, album_name=args.album, 
                        artist=args.artist if args.artist else None)

    elif args.commands == 'print':
        if args.playlist:
            spotify.print_playlists()
        elif args.track:
            spotify.print_tracklist(args.track)

    elif args.commands == 'delete_track':
        spotify.delete_track(args.track, args.playlist)

    elif args.commands == 'delete_album':
        spotify.delete_album(args.album, args.playlist)