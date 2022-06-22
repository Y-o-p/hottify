# Is a hidden import to pyinstaller 
import http.server

import requests
import spotipy
import keyboard
from spotipy.oauth2 import SpotifyPKCE
import json

class Hottify():
    def __init__(
        self, 
        previous_track='ctrl + alt + left',
        next_track='ctrl + alt + right',
        lower_volume='ctrl + alt + down',
        raise_volume='ctrl + alt + up',
        toggle_playback='ctrl + alt + space'
    ):
        self.device=None
        self._init_spotify()
        keyboard.add_hotkey(previous_track, self.prev_track)
        keyboard.add_hotkey(next_track, self.next_track)
        keyboard.add_hotkey(lower_volume, self.change_volume, (-5,))
        keyboard.add_hotkey(raise_volume, self.change_volume, (5,))
        keyboard.add_hotkey(toggle_playback, self.toggle_playback)

    def toggle_playback(self):
        playback_information = self._handle_api_call(self.sp.current_playback)
        if playback_information is None:
            print("ERROR no playback information: trying to start playback anyways...")
            self._handle_api_call(self.sp.start_playback, (self.device,))
            return
        is_playing = playback_information["is_playing"]
        if is_playing:
            self._handle_api_call(self.sp.pause_playback, (self.device,))
        else:
            self._handle_api_call(self.sp.start_playback, (self.device,))

    def prev_track(self):
        self._handle_api_call(self.sp.previous_track, (self.device,))

    def next_track(self):
        self._handle_api_call(self.sp.next_track, (self.device,))

    def change_volume(self, amount: int):
        playback_information = self._handle_api_call(self.sp.current_playback)
        if playback_information is None:
            return
        print(playback_information)
        current_volume = playback_information['device']['volume_percent']
        self._handle_api_call(self.sp.volume, (current_volume + amount, self.device))

    def set_active_device(self, device: str):
        self.device = device

    def get_possible_devices(self) -> list:
        return self._handle_api_call(self.sp.devices)

    def _init_spotify(self) -> spotipy.Spotify:
        scope = "user-read-recently-played user-modify-playback-state user-read-playback-state"
        client_id = 'edf8b38c6fa84240b46216412e213525'
        redirect_uri = 'http://localhost:6969/'

        auth_manager = SpotifyPKCE(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
        self.sp = spotipy.Spotify(oauth_manager=auth_manager, auth_manager=auth_manager)

    def _handle_api_call(self, func, args=(), retry_if_conn_err=True):
        try:
            return func(*args)
        except spotipy.exceptions.SpotifyException as e:
            print(e)
            return None
        except requests.exceptions.ConnectionError as e:
            print(e)
            self._init_spotify()
            if retry_if_conn_err:
                self._handle_api_call(func, args, False)

prog = Hottify()
device_id = None
try:
    file = open("settings.json", "r")
    settings = json.loads(file.read())
    file.close()
    device_id = settings["device_id"]
    prog.set_active_device(device_id)
except FileNotFoundError as err:
    devices = prog.get_possible_devices()["devices"]
    for device in devices:
        if device["is_active"]:
            print(f'Found active device {device["name"]}')
            device_id = device["id"]
            prog.set_active_device(device_id)
            content = {
                "device_id": device_id,
                "volume_change": 5,
            }
            file = open("settings.json", "w")
            file.write(json.dumps(content))
            file.close()
        elif device == devices[-1]:
            raise spotipy.exceptions.SpotifyException("Could not find an active device to sync with...")

keyboard.wait('ctrl + alt + q')