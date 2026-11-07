"""SYNTH: R1~R7의 가짜 HTTP 응답. 실제 GET·소켓 사용 없음."""
import importlib
import struct
import sys
from pathlib import Path
from unittest.mock import patch

from tests._pt_support import NetworkBlockedCase

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class FetchTests(NetworkBlockedCase):
    def setUp(self):
        super().setUp()
        self.fetch = importlib.import_module("plating_tools.refs.fetch")
        self.jpeg = b"\xff\xd8\xff\xc0\x00\x11\x08\x00\x10\x00\x20\x03" + b"\x01\x11\x00" * 3 + b"\xff\xd9"

    def test_R1_jpeg_header(self):
        result = self.fetch.inspect_response(200, "image/jpeg", self.jpeg, "https://synth.invalid")
        self.assertEqual(result.error.value, "none")
        self.assertEqual((result.image.width, result.image.height), (32, 16))

    def test_R2_R3_R6_response_failures(self):
        for status, content, body, expected in ((200, "text/html", b"<html>SYNTH</html>", "html_page"), (403, "image/jpeg", self.jpeg, "http_status"), (404, "image/jpeg", self.jpeg, "http_status"), (200, "image/png", b"<html>SYNTH</html>", "not_image")):
            self.assertEqual(self.fetch.inspect_response(status, content, body, "https://synth.invalid").error.value, expected)

    def run_fake(self, responses, **limits):
        calls = []
        class Response:
            def __init__(inner, item):
                inner.status, inner.headers, inner.body = item
                inner.offset = 0
            def read(inner, size):
                result = inner.body[inner.offset:inner.offset + size]
                inner.offset += len(result)
                return result
            def __enter__(inner): return inner
            def __exit__(inner, *args): return False
        def open_fake(request, timeout):
            calls.append(request)
            item = responses[len(calls) - 1]
            if isinstance(item, Exception): raise item
            return Response(item)
        with patch("plating_tools.refs.fetch.build_opener") as build:
            build.return_value.open.side_effect = open_fake
            result = self.fetch.UrllibFetcher().get("https://synth.invalid/start", timeout_s=2, max_redirects=limits.get("max_redirects", 2), max_bytes=limits.get("max_bytes", 1024))
        return result, calls

    def test_R4_timeout(self):
        result, _ = self.run_fake([TimeoutError("SYNTH")])
        self.assertEqual(result.error.value, "timeout")

    def test_R5_redirect_limit_and_https_at_every_hop(self):
        redirect = (302, {"Location": "/image"}, b"")
        success = (200, {"Content-Type": "image/jpeg"}, self.jpeg)
        result, calls = self.run_fake([redirect, success], max_redirects=1)
        self.assertEqual(result.error.value, "none")
        self.assertEqual(len(calls), 2)
        result, calls = self.run_fake([redirect], max_redirects=0)
        self.assertEqual(result.error.value, "too_many_redirects")
        result, calls = self.run_fake([(302, {"Location": "http://synth.invalid"}, b"")])
        self.assertEqual(result.error.value, "non_https")
        self.assertEqual(len(calls), 1)

    def test_R7_reads_only_limit_plus_one(self):
        result, _ = self.run_fake([(200, {"Content-Type": "image/jpeg"}, self.jpeg * 100)], max_bytes=16)
        self.assertEqual(result.error.value, "too_large")
        self.assertEqual(result.body_size, 17)

    def test_webp_header_variants(self):
        images = importlib.import_module("plating_tools.refs.images")
        vp8x = b"\0" * 4 + (31).to_bytes(3, "little") + (15).to_bytes(3, "little")
        vp8l = b"\x2f" + (31 | (15 << 14)).to_bytes(4, "little")
        vp8 = b"\0\0\0\x9d\x01\x2a" + struct.pack("<HH", 32, 16)
        for kind, payload in ((b"VP8X", vp8x), (b"VP8L", vp8l), (b"VP8 ", vp8)):
            body = b"RIFF" + struct.pack("<I", 12 + len(payload)) + b"WEBP" + kind + struct.pack("<I", len(payload)) + payload
            image = images.inspect_image(body)
            self.assertEqual((image.width, image.height), (32, 16))
