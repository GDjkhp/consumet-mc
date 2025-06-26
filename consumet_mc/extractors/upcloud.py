from __future__ import annotations
import json
import re


from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.models.source import Source
from consumet_mc.models.subtitle import Subtitle
from consumet_mc.models.video import Video
from consumet_mc.utils import crypto


class Upcloud(VideoExtractor):
    def extract(self) -> Source:
        videos = []
        subtitles = []
        try:
            headers = {"Referer": self.server.url, "X-Requested-With": "XMLHttpRequest"}
            base_url_regx = r"https://[a-zA-Z0-9.]*"
            match = re.match(base_url_regx, self.server.url)
            if not match:
                return Source([])
            base_url = match.group(0)
            parts = self.server.url.split("/")
            last_part = parts[-1]
            id = last_part.split("?")[0]
            url = f"{base_url}/embed-1/v2/e-1/getSources?id={id}"
            response = self.http_client.request("GET", url, headers=headers)
            response.raise_for_status()

            data = response.json()

            sources_encrypted = data["sources"]
            sources = None
            aes_keys = []

            aes_keys.append(self._get_aes_key1())
            aes_keys.append(self._get_aes_key2())

            for aes_key in aes_keys:
                try:
                    if aes_key:
                        sources_json_str = self._decrypte_sources(
                            sources_encrypted, aes_key
                        )
                        sources = json.loads(sources_json_str)
                        break
                except Exception:
                    pass

            if not sources:
                raise Exception(f"Failed to decrypted source url:{sources_encrypted}")

            tracks = data["tracks"]
            video_url = sources[0]["file"]
            video_type = sources[0]["type"]
            is_m3u8 = True if "hls" in video_type else False

            for track in tracks:
                if "label" in track:
                    subtitles.append(Subtitle(track["file"], track["label"]))
            videos.append(Video(video_url, is_m3u8))

            return Source(
                videos, subtitles, {"referer": self.server.url.split("embed")[0]}
            )

        except Exception as e:
            raise e

    def _get_aes_key1(self):
        url = "https://keys.hs.vc/"
        response = self.http_client.request("GET", url)
        response.raise_for_status()

        aes_key = None
        if response.status_code == 200:
            data = response.json()
            if data["rabbitstream"]["success"]:
                aes_key = data["rabbitstream"]["key"]
        return aes_key

    def _get_aes_key2(self):
        url = "https://key.hi-anime.site/"
        response = self.http_client.request("GET", url)
        response.raise_for_status()

        aes_key = None
        if response.status_code == 200:
            data = response.json()
            aes_key = data["rabbit"]
        return aes_key

    def _decrypte_sources(self, sources: str, key: str):
        try:
            decrypted = crypto.aes_decrypt(sources, key)
            return decrypted
        except Exception as e:
            raise Exception(f"Failed to decrypted source url:{e}")
