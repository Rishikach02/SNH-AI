"""
HTTP server exposing the tree management API.
"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from . import config, db, tree_service


class TreeRequestHandler(BaseHTTPRequestHandler):
    server_version = "TreeAPI/1.0"
    protocol_version = "HTTP/1.1"

    def _send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, status: HTTPStatus, message: str) -> None:
        self._send_json({"error": message, "status": status.value}, status=status)

    def _read_json_body(self) -> Any:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            raise ValueError("Request body is required")
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Request body must be valid JSON") from exc

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler naming)
        if self.path == "/api/tree":
            self.handle_list_trees()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/tree":
            self.handle_create_node()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    def handle_list_trees(self) -> None:
        trees = [node.to_dict() for node in tree_service.list_trees()]
        self._send_json(trees)

    def handle_create_node(self) -> None:
        try:
            payload = self._read_json_body()
        except ValueError as exc:
            self._send_error_json(HTTPStatus.BAD_REQUEST, str(exc))
            return

        label = payload.get("label")
        parent_id = payload.get("parent_id")
        if parent_id is not None:
            try:
                parent_id = int(parent_id)
            except (TypeError, ValueError):
                self._send_error_json(HTTPStatus.BAD_REQUEST, "parent_id must be an integer")
                return

        try:
            node = tree_service.create_node(label=label, parent_id=parent_id)
        except tree_service.ValidationError as exc:
            self._send_error_json(HTTPStatus.BAD_REQUEST, str(exc))
            return
        except tree_service.NodeNotFound as exc:
            self._send_error_json(HTTPStatus.NOT_FOUND, str(exc))
            return
        except Exception as exc:  # pragma: no cover - defensive logging
            self.log_error("Unexpected error: %s", exc)
            self._send_error_json(HTTPStatus.INTERNAL_SERVER_ERROR, "Unexpected server error")
            return

        self._send_json(node.to_dict(), status=HTTPStatus.CREATED)

    def log_message(self, fmt: str, *args: Any) -> None:
        # Route logs to stdout for easier container capture
        message = "%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), fmt % args)
        print(message, end="")


def run_server() -> None:
    db.initialize()
    address = (config.HOST, config.PORT)
    with ThreadingHTTPServer(address, TreeRequestHandler) as httpd:
        print(f"Serving on http://{config.HOST}:{config.PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
