from __future__ import annotations

import base64
import json
import re

import requests

from consumet_mc.models.source import Source
from consumet_mc.models.subtitle import Subtitle
from consumet_mc.extractors.video_extractor import VideoExtractor
from consumet_mc.models.video import Video


class Voe(VideoExtractor):
    def extract(self) -> Source:
        videos = []
        subtitles = []
        try:
            referer = str(self.server.extra_data["referer"])
            headers = {"Referer": referer}
            response = self.http_client.request("GET", self.server.url, headers=headers)
            response.raise_for_status()
            page_url_regex = r"window\.location\.href = '(?P<url>[^']+)'"
            match = re.search(page_url_regex, response.text)
            if not match:
                return Source([])
            page_url = match.group(1)
            response = requests.get(page_url)
            response.raise_for_status()
            encoded_str_regex = (
                r"<script type=\"application/json\">.*\[(.*?)\]</script>"
            )
            match = re.search(encoded_str_regex, response.text)
            if not match:
                return Source([])
            encoded_str = match.group(1)
            data = self._decrypt_encoded_str(encoded_str)
            if data:
                site_name = data["site_name"]
                video_url = data["source"]
                for sub in data["captions"]:
                    subtitles.append(
                        Subtitle(f"https://{site_name}{sub['file']}", sub["label"])
                    )
                videos.append(Video(video_url, True if "m3u8" in video_url else False))

            return Source(videos, subtitles)
        except Exception as e:
            raise e

    def _rot13(self, s: str):
        result = []
        for c in s:
            if "A" <= c <= "Z":
                result.append(chr((ord(c) - ord("A") + 13) % 26 + ord("A")))
            elif "a" <= c <= "z":
                result.append(chr((ord(c) - ord("a") + 13) % 26 + ord("a")))
            else:
                result.append(c)
        return "".join(result)

    def _replace_pattern(self, s: str):
        patterns = ["@$", "^^", "~@", "%?", "*~", "!!", "#&"]
        result = s
        for pattern in patterns:
            escaped_pattern = re.escape(pattern)
            result = re.sub(escaped_pattern, "_", result)
        return result

    def _remove_underscores(self, s: str) -> str:
        return s.replace("_", "")

    def _char_shift(self, s: str, shift: int) -> str:
        return "".join(chr(ord(c) - shift) for c in s)

    def _reverse(self, s: str) -> str:
        return s[::-1]

    def _base64_decode(self, s: str) -> str:
        try:
            decoded_bytes = base64.b64decode(s)
            return decoded_bytes.decode("utf-8")
        except Exception as e:
            print("Base64 decode failed:", e)
            return ""

    def _decrypt_encoded_str(self, s):
        try:
            s1 = self._rot13(s)
            s2 = self._replace_pattern(s1)
            s3 = self._remove_underscores(s2)
            s4 = self._base64_decode(s3)
            s5 = self._char_shift(s4, 3)
            s6 = self._reverse(s5)
            s7 = self._base64_decode(s6)
            return json.loads(s7)
        except Exception as e:
            print("Decryption error: ", e)
            return {}
