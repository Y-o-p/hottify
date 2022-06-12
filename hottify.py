# Is a hidden import to pyinstaller 
import http.server

import requests
import spotipy
import keyboard
from spotipy.oauth2 import SpotifyPKCE

class Hottify():
    previous_track = 'ctrl + alt + left'
    next_track = 'ctrl + alt + right'
    lower_volume = 'ctrl + alt + down'
    raise_volume = 'ctrl + alt + up'
    toggle_playback = 'ctrl + alt + space'

    def __init__(
        self, 
        previous_track=previous_track,
        next_track=next_track,
        lower_volume=lower_volume,
        raise_volume=raise_volume,
        toggle_playback=toggle_playback
    ):
        self.sp = self._init_spotify()
        keyboard.add_hotkey(previous_track, self._handle_api_call, (self.sp.previous_track,))
        keyboard.add_hotkey(next_track, self._handle_api_call, (self.sp.next_track,))
        keyboard.add_hotkey(lower_volume, self.change_volume, (-5,))
        keyboard.add_hotkey(raise_volume, self.change_volume, (5,))
        keyboard.add_hotkey(toggle_playback, self.toggle_playback)

    def toggle_playback(self):
        playback_information = self._handle_api_call(self.sp.current_playback)
        if playback_information is None:
            return
        is_playing = playback_information["is_playing"]
        if is_playing:
            self._handle_api_call(self.sp.pause_playback)
        else:
            self._handle_api_call(self.sp.start_playback)

    def change_volume(self, amount: int):
        playback_information = self._handle_api_call(self.sp.current_playback)
        if playback_information is None:
            return
        current_volume = playback_information['device']['volume_percent']
        self._handle_api_call(self.sp.volume, (current_volume + amount,))

    def _init_spotify(self) -> spotipy.Spotify:
        scope = "user-read-recently-played user-modify-playback-state user-read-playback-state"
        client_id = 'edf8b38c6fa84240b46216412e213525'
        redirect_uri = 'http://localhost:6969/'

        auth_manager = SpotifyPKCE(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
        return spotipy.Spotify(oauth_manager=auth_manager, auth_manager=auth_manager)

    def _handle_api_call(self, func, args=(), retry_if_conn_err=True):
        try:
            return func(*args)
        except spotipy.exceptions.SpotifyException as e:
            print(e)
            return None
        except requests.exceptions.ConnectionError as e:
            print(e)
            self.sp = self._init_spotify()
            if retry_if_conn_err:
                self._handle_api_call(func, args, False)

prog = Hottify()
keyboard.wait('ctrl + alt + q')