import base64
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from pathlib import Path
from urllib import error, parse, request

from flask import current_app


GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
GMAIL_SEND_ENDPOINT = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


class EmailServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass(slots=True)
class GmailClientConfig:
    client_id: str
    client_secret: str
    auth_uri: str
    token_uri: str
    redirect_uris: list[str]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    candidate = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _read_json_file(file_path: Path, missing_message: str) -> dict:
    if not file_path.exists():
        raise EmailServiceError(missing_message, 400)
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EmailServiceError(f"File JSON tidak valid: {file_path}", 400) from exc


def _build_http_error_message(http_error: error.HTTPError, prefix: str) -> str:
    try:
        payload = json.loads(http_error.read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        payload = None

    detail = None
    if isinstance(payload, dict):
        error_payload = payload.get("error")
        if isinstance(error_payload, dict):
            detail = error_payload.get("message")
        elif isinstance(error_payload, str):
            detail = error_payload
    return f"{prefix}: {detail or http_error.reason}"


def _load_gmail_client_config() -> GmailClientConfig:
    client_secret_path = current_app.config.get("GMAIL_CLIENT_SECRET_PATH")
    if not client_secret_path:
        raise EmailServiceError(
            "Path client secret Gmail belum diatur. Isi GMAIL_CLIENT_SECRET_PATH terlebih dahulu.",
            400,
        )

    payload = _read_json_file(
        Path(client_secret_path),
        "File client secret Gmail tidak ditemukan.",
    )
    config_data = payload.get("web") or payload.get("installed")
    if not isinstance(config_data, dict):
        raise EmailServiceError(
            "Format client secret Gmail tidak dikenali. Gunakan JSON OAuth dari Google Cloud.",
            400,
        )

    client_id = config_data.get("client_id")
    client_secret = config_data.get("client_secret")
    auth_uri = config_data.get("auth_uri")
    token_uri = config_data.get("token_uri")

    if not all([client_id, client_secret, auth_uri, token_uri]):
        raise EmailServiceError("Client secret Gmail belum lengkap.", 400)

    return GmailClientConfig(
        client_id=client_id,
        client_secret=client_secret,
        auth_uri=auth_uri,
        token_uri=token_uri,
        redirect_uris=list(config_data.get("redirect_uris") or []),
    )


def _token_path() -> Path:
    return Path(current_app.config["GMAIL_TOKEN_PATH"])


def _save_token(token_payload: dict) -> dict:
    token_path = _token_path()
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(
        json.dumps(token_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return token_payload


def _load_token() -> dict:
    return _read_json_file(
        _token_path(),
        "Token Gmail belum tersedia. Jalankan skrip setup_gmail_token.py terlebih dahulu.",
    )


def _request_token(token_uri: str, payload: dict) -> dict:
    encoded = parse.urlencode(payload).encode("utf-8")
    http_request = request.Request(
        token_uri,
        data=encoded,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise EmailServiceError(
            _build_http_error_message(exc, "Gagal meminta token OAuth Gmail"),
            exc.code,
        ) from exc
    except error.URLError as exc:
        raise EmailServiceError(f"Gagal terhubung ke layanan OAuth Gmail: {exc.reason}", 502) from exc


def build_gmail_authorization_url(state: str | None = None) -> str:
    client_config = _load_gmail_client_config()
    redirect_uri = current_app.config["GMAIL_OAUTH_REDIRECT_URI"]

    params = {
        "client_id": client_config.client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": GMAIL_SEND_SCOPE,
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent",
    }
    if state:
        params["state"] = state
    return f"{client_config.auth_uri}?{parse.urlencode(params)}"


def exchange_google_authorization_code(code: str) -> dict:
    client_config = _load_gmail_client_config()
    redirect_uri = current_app.config["GMAIL_OAUTH_REDIRECT_URI"]

    token_response = _request_token(
        client_config.token_uri,
        {
            "code": code,
            "client_id": client_config.client_id,
            "client_secret": client_config.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    refresh_token = token_response.get("refresh_token")
    if not refresh_token:
        raise EmailServiceError(
            "Google tidak mengembalikan refresh token. Pastikan prompt consent dipakai dan akses offline diizinkan.",
            400,
        )

    expires_in = int(token_response.get("expires_in", 3600))
    return _save_token(
        {
            "access_token": token_response["access_token"],
            "refresh_token": refresh_token,
            "token_type": token_response.get("token_type", "Bearer"),
            "scope": token_response.get("scope", GMAIL_SEND_SCOPE),
            "expires_at": (_utcnow() + timedelta(seconds=expires_in)).isoformat(),
            "token_uri": client_config.token_uri,
        }
    )


def _refresh_access_token_if_needed() -> dict:
    client_config = _load_gmail_client_config()
    token_payload = _load_token()
    expires_at = _parse_iso_datetime(token_payload.get("expires_at"))

    if expires_at and expires_at > (_utcnow() + timedelta(seconds=60)):
        return token_payload

    refresh_token = token_payload.get("refresh_token")
    if not refresh_token:
        raise EmailServiceError(
            "Refresh token Gmail tidak tersedia. Jalankan ulang setup_gmail_token.py.",
            400,
        )

    refreshed = _request_token(
        client_config.token_uri,
        {
            "client_id": client_config.client_id,
            "client_secret": client_config.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )
    expires_in = int(refreshed.get("expires_in", 3600))

    token_payload["access_token"] = refreshed["access_token"]
    token_payload["token_type"] = refreshed.get("token_type", token_payload.get("token_type", "Bearer"))
    token_payload["scope"] = refreshed.get("scope", token_payload.get("scope", GMAIL_SEND_SCOPE))
    token_payload["expires_at"] = (_utcnow() + timedelta(seconds=expires_in)).isoformat()
    return _save_token(token_payload)


def send_gmail_email(*, recipient_email: str, subject: str, body: str) -> dict:
    token_payload = _refresh_access_token_if_needed()
    sender_email = current_app.config.get("GMAIL_SENDER_EMAIL")

    mime_message = MIMEText(body, _subtype="plain", _charset="utf-8")
    mime_message["To"] = recipient_email
    if sender_email:
        mime_message["From"] = sender_email
    mime_message["Subject"] = subject

    raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode("utf-8")
    http_request = request.Request(
        GMAIL_SEND_ENDPOINT,
        data=json.dumps({"raw": raw_message}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token_payload['access_token']}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise EmailServiceError(
            _build_http_error_message(exc, "Gagal mengirim email Gmail"),
            exc.code,
        ) from exc
    except error.URLError as exc:
        raise EmailServiceError(f"Gagal terhubung ke Gmail API: {exc.reason}", 502) from exc
