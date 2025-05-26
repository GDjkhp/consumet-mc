from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from consumet_mc.extractors.utils.aes_cipher import AESCipher

if TYPE_CHECKING:
    from mov_cli.http_client import HTTPClient

from .video_extractor import StreamingServer, Video, VideoExtractor, Subtitle
from ctypes import c_int32


class KK(VideoExtractor):
    def __init__(self, http_client: HTTPClient) -> None:
        super().__init__(http_client)
        self._subGuid = "VgV52sWhwvBSf8BsM3BRY9weWiiCbtGp"
        self._viGuid = "62f176f3bb1b5b8e70e39932ad34a0c7"
        self._appVer = "2.8.10"
        self._platformVer = "4830201"
        self._appName = "kisskh"
        self._aes_key = "4f6bdaa39E2F8CB07f5e722d9EDEF314"
        self._aes_iv = "01504af356e619cf2e42bba68C3F70F9"
        self._cipher = AESCipher(self._aes_key, self._aes_iv, True)

    @property
    def server_name(self) -> StreamingServer:
        return StreamingServer.KK

    def extract(self, url: str, **kwargs) -> list[Video]:
        episode_id = str(kwargs["episode_id"])
        kk_vid_key = [
            "",
            episode_id,
            "",
            "mg3c3b04ba",
            self._appVer,
            self._viGuid,
            self._platformVer,
            self._appName,
            self._appName,
            self._appName,
            self._appName,
            self._appName,
            self._appName,
            "00",
            "",
        ]
        kk_subs_key = [
            "",
            episode_id,
            "",
            "mg3c3b04ba",
            self._appVer,
            self._subGuid,
            self._platformVer,
            self._appName,
            self._appName,
            self._appName,
            self._appName,
            self._appName,
            self._appName,
            "00",
            "",
        ]

        kk_vid_key_word = self._calculate_hash("|".join(kk_vid_key))
        kk_subs_key_word = self._calculate_hash("|".join(kk_subs_key))

        kk_vid_key.insert(1, str(kk_vid_key_word))
        kk_subs_key.insert(1, str(kk_subs_key_word))

        encrypted_subs_key = (
            base64.b64decode(self._cipher.encrypt("|".join(kk_subs_key))).hex().upper()
        )
        encrypted_vid_key = (
            base64.b64decode(self._cipher.encrypt("|".join(kk_vid_key))).hex().upper()
        )

        vid_data_url = f"{url}?kkey={encrypted_vid_key}"
        subs_data_url = f"{kwargs['subs_url']}?kkey={encrypted_subs_key}"

        vid_data_response = self.http_client.get(vid_data_url)
        subs_data_reponse = self.http_client.get(subs_data_url)

        vid_data_response.raise_for_status()

        vid_data = vid_data_response.json()
        video = Video(vid_data["Video"], False)

        if subs_data_reponse.status_code == 200:
            subs_data = subs_data_reponse.json()
            subs = []
            for sub_data in subs_data:
                subtitle = Subtitle(sub_data["src"], sub_data["label"])
                subs.append((subtitle))
            video.subtitles = subs

        return [video]

    def _calculate_hash(self, token_str: str):
        word = 0

        for i in range(len(token_str)):
            word = c_int32((word << 5)).value - word + ord(token_str[i])

        return word
