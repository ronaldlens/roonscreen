import sys
import pprint

import requests
import roonapi
from PySide6.QtGui import QImage, QPixmap, QScreen
from roonapi import RoonApi, RoonDiscovery
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton

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
    _album_art = None
    _walbum = None
    _album_height = None

    def __init__(self):
        super().__init__()
        print("starting main window")
        self.setWindowTitle("Roon Screen")
        scrGeometry = QScreen.availableGeometry(QApplication.primaryScreen())
        self.setGeometry(scrGeometry)
        self._album_height = scrGeometry.height()-40
        self._walbum = QLabel(self)
        self._walbum.setGeometry(20,20, self._album_height, self._album_height)


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

    def state_callback(self, event, changed_ids):
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
            self._album_art = image_key
            self.update_album()

    def update_album(self):
        img_url = self._roonapi.get_image(self._album_art, width=self._album_height, height=self._album_height)
        img = QImage()
        img.loadFromData(requests.get(img_url).content)
        self._walbum.setPixmap(QPixmap.fromImage(img))

print("starting Roonscreen")
app = QApplication(sys.argv)
window = MainWindow()
window.init_roon()
window.wop()
window.show()
app.exec()
