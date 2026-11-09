import sys
import pprint

import requests
from PySide6.QtGui import QImage, QPixmap, QScreen
from roonapi import RoonApi, RoonDiscovery
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy, QStyle, QPushButton
from PySide6.QtCore import Qt

appinfo = {
    "extension_id": "Ronald's roon screen",
    "display_name": "screen for roon",
    "display_version": "1.0",
    "publisher": "Ronald",
    "email": "ronald@ronald.com"
}


class MainWindow(QMainWindow):
    _token = None
    _core_id = None
    _zone_id = None
    _output_id = None
    _roonapi = None
    _song_name = None
    _album = None
    _artist = None
    _album_art = None
    _album_height = None
    _w_album_img = None
    _w_song = None
    _w_album = None
    _w_artist = None
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Roon Screen")
        scrGeometry = QScreen.availableGeometry(QApplication.primaryScreen())
        print(scrGeometry.width())
        print(scrGeometry.height())
        self.setGeometry(0,0,1024,1080)
        self._album_height = scrGeometry.height()-60
        self._w_album_img = QLabel()
        self._w_album_img.setFixedSize(self._album_height, self._album_height)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self._w_album_img)

        v1layout = QVBoxLayout()
        v1layout.setSpacing(30)
        self._w_song = QLabel()
        self._w_song.setAlignment(Qt.AlignCenter)
        self._w_song.setStyleSheet("font-size: 64px; font-weight: bold;")
        self._w_artist = QLabel()
        self._w_artist.setAlignment(Qt.AlignCenter)
        self._w_artist.setStyleSheet("font-size: 56px; font-weight: bold;")
        self._w_album = QLabel()
        self._w_album.setAlignment(Qt.AlignCenter)
        self._w_album.setStyleSheet("font-size: 56px; font-weight: bold;")
        filler1 = QWidget()
        filler1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        v1layout.addWidget(self._w_song)
        v1layout.addWidget(self._w_artist)
        v1layout.addWidget(self._w_album)
        v1layout.addWidget(filler1)
        main_layout.addLayout(v1layout)
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def init_roon(self):
        print("setting up roon")
        try:
            self._token = open("my_token_file").read()
            self._core_id = open("my_core_id_file").read()
            self._zone_id = open("my_zone_id").read()
            self._output_id = open("my_output_id").read()


        except FileNotFoundError:
            print("File not found")
        discover = RoonDiscovery(self._core_id)
        server = discover.first()
        discover.stop()

        self._roonapi = RoonApi(appinfo, self._token, server[0], server[1], True)
        self._roonapi.register_state_callback(self.state_callback)

        print(self._zone_id)

    def state_callback(self, _event, _changed_ids):
        self.get_info()


    def wop(self):
        print("wop")
        #zone = self._roonapi.zone_by_name("WiiM").values()
        zone = self._roonapi.zone_by_output_id(self._output_id)
        pp = pprint.PrettyPrinter(indent=4)

        pp.pprint(zone)
        #print(zone["now_playing"]["three_line"])
        # for zone in self._roonapi.zones.values():
        #     if zone["zone_id"] == self._zone_id:
        #         print(zone["now_playing"]["three_line"])
        #         print(zone)

    def get_info(self):
        zone = self._roonapi.zone_by_output_id(self._output_id)
        now_playing = zone["now_playing"]
        artis_image_key = now_playing["artist_image_keys"][0]
        image_key = now_playing["image_key"]
        three_line = now_playing["three_line"]
        song = three_line["line1"]
        artist = three_line["line2"]
        album = three_line["line3"]
        length = now_playing["length"]
        seek_pos = now_playing["seek_position"]
        if self._song_name != song:
            self._song_name = song
            self._album = album
            self._artist = artist
            self._album_art = image_key
            self.update_album()

    def update_album(self):
        img_url = self._roonapi.get_image(self._album_art, width=self._album_height, height=self._album_height)
        img = QImage()
        img.loadFromData(requests.get(img_url).content)
        self._w_album_img.setPixmap(QPixmap.fromImage(img))
        self._w_song.setText(self._song_name)
        self._w_artist.setText(self._artist)
        self._w_album.setText(self._album)

print("starting Roonscreen")
app = QApplication(sys.argv)
window = MainWindow()
window.init_roon()
window.wop()
window.show()
app.exec()
