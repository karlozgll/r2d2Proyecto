import os
import sys
import json
import webbrowser
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

class Spotipy:
    def __init__(self):
        self.credenciales = SpotifyClientCredentials(client_id='b5924bbeaf264a4282714853c1c88df1',client_secret='dadf746b9f2e4884a635f58e6099bc04')
        self.SP_obj = spotipy.Spotify(client_credentials_manager=self.credenciales)

    def busqueda_cancion(self,nombre_cancion,nombre_tipo='track'):
        lista=[]
        results= self.SP_obj.search(nombre_cancion,type=nombre_tipo)
        for e in results['tracks']['items']:
            lista.append([e['name'],e['id'],str(e['preview_url']),e['album']['images'][0]['url'],e['uri']])
        return lista