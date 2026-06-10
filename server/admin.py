import html
import logging
import os
import secrets
import time
import tomllib
from collections import defaultdict
from pathlib import Path

import settings as _settings
from fastapi import APIRouter, Cookie, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

logger = logging.getLogger("server.admin")
router = APIRouter()

_PASSWORD_FILE = Path(os.getenv("ADMIN_PASSWORD_FILE", "./admin_password"))

try:
    _PASSWORD: str | None = _PASSWORD_FILE.read_text(encoding="utf-8").strip() or None
    if _PASSWORD is None:
        logger.error(
            "Admin password file at %s is empty — admin UI disabled.",
            _PASSWORD_FILE.resolve(),
        )
except FileNotFoundError:
    logger.error(
        """
        Admin password file not found at %s — admin UI disabled. 
        Create the file with a password and restart.
        """,
        _PASSWORD_FILE.resolve(),
    )

_sessions: set[str] = set()

_MAX_FAILURES = 5
_WINDOW = 300  # rolling window in seconds; IP is unblocked once all failures age out
_failure_log: dict[str, list[float]] = defaultdict(list)


def _get_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _is_rate_limited(ip: str) -> bool:
    now = time.monotonic()
    _failure_log[ip] = [t for t in _failure_log[ip] if now - t < _WINDOW]
    return len(_failure_log[ip]) >= _MAX_FAILURES


def _record_failure(ip: str) -> None:
    _failure_log[ip].append(time.monotonic())


def _is_authenticated(session: str | None) -> bool:
    return bool(session and session in _sessions)


# CSS is a plain string (not an f-string) so the curly braces in CSS rules are safe.
_STYLE = """<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,sans-serif;background:#f5f5f5;color:#222;line-height:1.5}
.card{max-width:380px;margin:80px auto;background:#fff;border-radius:8px;padding:2rem;
box-shadow:0 2px 8px rgba(0,0,0,.12)}
.wrap{max-width:860px;margin:2rem auto;background:#fff;border-radius:8px;padding:2rem;
box-shadow:0 2px 8px rgba(0,0,0,.12)}
h1{font-size:1.3rem;margin-bottom:1.5rem}
input[type=password]{width:100%;padding:.55rem .75rem;border:1px solid #ccc;
border-radius:4px;font-size:1rem;margin-bottom:.9rem}
textarea{width:100%;height:62vh;padding:.6rem .75rem;border:1px solid #ccc;
border-radius:4px;font-family:monospace;font-size:.82rem;resize:vertical}
button{padding:.55rem 1.2rem;background:#2563eb;color:#fff;border:none;
border-radius:4px;cursor:pointer;font-size:.95rem}
button:hover{background:#1d4ed8}
.row{display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem}
.actions{display:flex;gap:1rem;align-items:center;margin-top:.9rem}
a{color:#2563eb;font-size:.9rem;text-decoration:none}
a:hover{text-decoration:underline}
.err{color:#dc2626;font-size:.9rem}
.ok{color:#16a34a;font-size:.9rem}
</style>"""


def _disabled_page() -> HTMLResponse:
    return HTMLResponse(
        """<!DOCTYPE html><html lang='no'><head><meta charset='utf-8'>
        <title>OS-bot Admin</title>" + _STYLE + "</head><body>
        <div class='card'><h1>OS-bot Admin</h1>
        <p class='err'>
            Admin-grensesnittet er deaktivert. Passordfil mangler eller er tom. 
            Se serverloggene.
        </p>
        </div></body></html>""",
        status_code=503,
    )


def _login_page(error: str = "") -> HTMLResponse:
    err = f'<p class="err">{html.escape(error)}</p>' if error else ""
    return HTMLResponse(
        "<!DOCTYPE html><html lang='no'><head><meta charset='utf-8'>"
        "<title>OS-bot Admin</title>" + _STYLE + "</head><body>"
        "<div class='card'><h1>OS-bot Admin</h1>"
        "<form method='post' action='/admin/login'>"
        "<input type='password' name='password' placeholder='Passord'"
        " autofocus autocomplete='current-password'>"
        "<button type='submit'>Logg inn</button>" + err + "</form></div></body></html>"
    )


def _editor_page(
    content: str, message: str = "", is_error: bool = False
) -> HTMLResponse:
    msg = ""
    if message:
        cls = "err" if is_error else "ok"
        msg = f'<span class="{cls}">{html.escape(message)}</span>'
    safe = html.escape(content)
    return HTMLResponse(
        "<!DOCTYPE html><html lang='no'><head><meta charset='utf-8'>"
        "<title>OS-bot Admin – Innstillinger</title>" + _STYLE + "</head><body>"
        "<div class='wrap'>"
        "<div class='row'>"
        "<h1>Innstillinger</h1><a href='/admin/logout'>Logg ut</a></div>"
        "<form method='post' action='/admin/settings'>"
        "<textarea name='content' spellcheck='false'>" + safe + "</textarea>"
        "<div class='actions'><button type='submit'>Lagre</button>" + msg + "</div>"
        "</form></div></body></html>"
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_get(session: str | None = Cookie(default=None)):
    if _PASSWORD is None:
        return _disabled_page()
    if not _is_authenticated(session):
        return RedirectResponse("/admin/login", status_code=302)
    content = _settings.path().read_text(encoding="utf-8")
    return _editor_page(content)


@router.get("/admin/login", response_class=HTMLResponse)
async def login_get(session: str | None = Cookie(default=None)):
    if _PASSWORD is None:
        return _disabled_page()
    if _is_authenticated(session):
        return RedirectResponse("/admin", status_code=302)
    return _login_page()


@router.post("/admin/login")
async def login_post(request: Request, password: str = Form(...)):
    if _PASSWORD is None:
        return _disabled_page()
    ip = _get_ip(request)
    if _is_rate_limited(ip):
        return _login_page("For mange forsøk. Prøv igjen om noen minutter.")
    if not secrets.compare_digest(password, _PASSWORD):
        _record_failure(ip)
        return _login_page("Feil passord.")
    token = secrets.token_urlsafe(32)
    _sessions.add(token)
    response = RedirectResponse("/admin", status_code=302)
    response.set_cookie("session", token, httponly=True, samesite="lax")
    return response


@router.get("/admin/logout")
async def logout(session: str | None = Cookie(default=None)):
    if session:
        _sessions.discard(session)
    response = RedirectResponse("/admin/login", status_code=302)
    response.delete_cookie("session")
    return response


@router.post("/admin/settings", response_class=HTMLResponse)
async def settings_post(
    request: Request,
    content: str = Form(...),
    session: str | None = Cookie(default=None),
):
    if _PASSWORD is None:
        return _disabled_page()
    if not _is_authenticated(session):
        return RedirectResponse("/admin/login", status_code=302)
    try:
        _settings.save(content)
    except tomllib.TOMLDecodeError as e:
        return _editor_page(content, f"Ugyldig TOML: {e}", is_error=True)
    except OSError as e:
        return _editor_page(content, f"Kunne ikke lagre: {e}", is_error=True)
    return _editor_page(content, "Innstillinger lagret.")
