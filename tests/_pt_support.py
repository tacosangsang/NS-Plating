"""P0 테스트 전용 네트워크 차단 기반 클래스."""
import unittest
from unittest.mock import patch


class NetworkBlockedCase(unittest.TestCase):
    def setUp(self):
        self.connections = self.enterContext(patch("socket.create_connection", side_effect=AssertionError("P0 네트워크 금지")))
        self.socket_connections = self.enterContext(patch("socket.socket.connect", side_effect=AssertionError("P0 네트워크 금지")))

    def tearDown(self):
        self.connections.assert_not_called()
        self.socket_connections.assert_not_called()
