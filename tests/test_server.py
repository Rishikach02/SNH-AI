from __future__ import annotations

import http.client
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from src import config, db, server, tree_service


class TreeServerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        config.DB_PATH = Path(self.tmpdir.name) / "server.db"
        db.initialize()
        tree_service.clear_all()

        self.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.TreeRequestHandler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        # give the server a moment to start
        time.sleep(0.05)

    def tearDown(self) -> None:
        self.httpd.shutdown()
        self.thread.join(timeout=1)
        self.httpd.server_close()
        self.tmpdir.cleanup()

    def _request(self, method: str, path: str, body: dict | None = None) -> tuple[int, dict, str]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = {}
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        conn.request(method, path, body=data, headers=headers)
        response = conn.getresponse()
        payload = response.read().decode("utf-8")
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            parsed = None
        conn.close()
        return response.status, parsed, payload

    def test_get_returns_empty_list(self) -> None:
        status, payload, _ = self._request("GET", "/api/tree")
        self.assertEqual(status, 200)
        self.assertEqual(payload, [])

    def test_post_creates_node(self) -> None:
        status, payload, _ = self._request("POST", "/api/tree", {"label": "root"})
        self.assertEqual(status, 201)
        self.assertEqual(payload["label"], "root")
        self.assertIsNotNone(payload["id"])
        self.assertEqual(payload["children"], [])

    def test_get_returns_nested_children(self) -> None:
        # create root and child via HTTP
        root_status, root_payload, _ = self._request("POST", "/api/tree", {"label": "root"})
        self.assertEqual(root_status, 201)
        child_status, _, _ = self._request(
            "POST",
            "/api/tree",
            {"label": "kid", "parent_id": root_payload["id"]},
        )
        self.assertEqual(child_status, 201)

        status, payload, _ = self._request("GET", "/api/tree")
        self.assertEqual(status, 200)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["label"], "root")
        self.assertEqual(payload[0]["children"][0]["label"], "kid")


if __name__ == "__main__":
    unittest.main()
