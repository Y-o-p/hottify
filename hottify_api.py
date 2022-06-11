import spotipy
import keyboard
from spotipy.oauth2 import SpotifyPKCE

scope = "user-read-recently-played user-modify-playback-state user-read-playback-state"
client_id = 'edf8b38c6fa84240b46216412e213525'
redirect_uri = 'http://localhost:6969/'

auth_manager = SpotifyPKCE(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
sp = spotipy.Spotify(oauth_manager=auth_manager)

def handle_api_call(func, args=()):
    try:
        if args:
            return func(*args)
        return func()
    except spotipy.exceptions.SpotifyException as e:
        print(e)
        return None

def toggle_playback():
    playback_information = handle_api_call(sp.current_playback)
    if playback_information is None:
        return
    is_playing = playback_information["is_playing"]
    if is_playing:
        handle_api_call(sp.pause_playback)
    else:
        handle_api_call(sp.start_playback)

def change_volume(amount: int):
    playback_information = handle_api_call(sp.current_playback)
    if playback_information is None:
        return
    current_volume = playback_information['device']['volume_percent']
    handle_api_call(sp.volume, (current_volume + amount,))

keyboard.add_hotkey('ctrl + alt + left', handle_api_call, (sp.previous_track,))
keyboard.add_hotkey('ctrl + alt + right', handle_api_call, (sp.next_track,))
keyboard.add_hotkey('ctrl + alt + down', change_volume, (-5,))
keyboard.add_hotkey('ctrl + alt + up', change_volume, (5,))
keyboard.add_hotkey('ctrl + alt + space', toggle_playback)

keyboard.wait('ctrl + alt + q')