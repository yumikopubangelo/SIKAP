import argparse
import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import parse


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Buat token OAuth Gmail untuk pengiriman email otomatis SIKAP.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Jangan buka browser otomatis. URL otorisasi tetap akan ditampilkan.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    os.environ.setdefault("GMAIL_CLIENT_SECRET_PATH", str(_detect_client_secret()))
    os.environ.setdefault("GMAIL_TOKEN_PATH", str(BACKEND_DIR / "instance" / "gmail_token.json"))
    os.environ.setdefault("GMAIL_OAUTH_REDIRECT_URI", "http://127.0.0.1:8765/oauth2callback")

    from app import create_app
    from app.services.email_service import (
        build_gmail_authorization_url,
        exchange_google_authorization_code,
    )

    app = create_app("development")
    with app.app_context():
        redirect_uri = app.config["GMAIL_OAUTH_REDIRECT_URI"]
        parsed_redirect = parse.urlparse(redirect_uri)
        if not parsed_redirect.hostname or not parsed_redirect.port:
            print("GMAIL_OAUTH_REDIRECT_URI harus mengandung host dan port loopback.")
            return 1

        auth_code: dict[str, str | None] = {"value": None}
        event = threading.Event()

        class OAuthCallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):  # noqa: N802
                query = parse.parse_qs(parse.urlparse(self.path).query)
                auth_code["value"] = query.get("code", [None])[0]
                if auth_code["value"]:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(
                        b"<html><body><h2>OAuth Gmail berhasil.</h2><p>Anda boleh menutup tab ini.</p></body></html>"
                    )
                else:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(
                        b"<html><body><h2>OAuth Gmail gagal.</h2><p>Kode otorisasi tidak ditemukan.</p></body></html>"
                    )
                event.set()

            def log_message(self, *_args, **_kwargs):  # noqa: D401
                return

        server = HTTPServer((parsed_redirect.hostname, parsed_redirect.port), OAuthCallbackHandler)
        server.timeout = 120

        url = build_gmail_authorization_url()
        print("Buka URL berikut untuk menyetujui akses Gmail:")
        print(url)
        print("")
        print(
            "Jika Google menolak redirect, tambahkan URI ini ke Google Cloud Console > Authorized redirect URIs:"
        )
        print(redirect_uri)
        if not args.no_browser:
            webbrowser.open(url)

        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()
        event.wait(timeout=180)
        server.server_close()

        if not auth_code["value"]:
            print("Kode otorisasi tidak diterima. Coba lagi setelah redirect URI diset di Google Cloud.")
            return 1

        token = exchange_google_authorization_code(auth_code["value"])
        print("Token Gmail berhasil disimpan ke:")
        print(app.config["GMAIL_TOKEN_PATH"])
        print("")
        print(json.dumps({"expires_at": token["expires_at"], "scope": token["scope"]}, ensure_ascii=False, indent=2))
    return 0


def _detect_client_secret() -> Path:
    matches = sorted(ROOT_DIR.glob("client_secret_*.apps.googleusercontent.com.json"))
    if not matches:
        raise FileNotFoundError("File client secret Gmail tidak ditemukan di root project.")
    return matches[0]


if __name__ == "__main__":
    raise SystemExit(main())
