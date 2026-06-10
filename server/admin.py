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
_PASSWORD: str | None = None

try:
    _text = _PASSWORD_FILE.read_text(encoding="utf-8").strip()
    if _text:
        _PASSWORD = _text
    else:
        logger.error(
            "Admin password file at %s is empty — admin UI disabled.",
            _PASSWORD_FILE.resolve(),
        )
except FileNotFoundError:
    logger.error(
        "Admin password file not found at %s — admin UI disabled. "
        "Create the file with a password and restart.",
        _PASSWORD_FILE.resolve(),
    )

_sessions: set[str] = set()
_MAX_FAILURES = 5
_WINDOW = 300  # rolling window in seconds; IP is unblocked once all failures age out
_failure_log: dict[str, list[float]] = defaultdict(list)

_ALL_CATEGORIES = [
    "RECALL",
    "CONCEPTUAL",
    "COMPARISON",
    "SYNTHESIS",
    "DEBUGGING",
    "PROCEDURE",
    "VERIFICATION",
    "NAVIGATIONAL",
]

# Plain string (not f-string) — CSS curly braces are literal here.
_STYLE = """\
<style>
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: system-ui, sans-serif;
    background: #f5f5f5;
    color: #222;
    line-height: 1.5;
  }
  .card {
    max-width: 380px;
    margin: 80px auto;
    background: #fff;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  }
  .wrap {
    max-width: 860px;
    margin: 2rem auto;
    background: #fff;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  }
  h1 { font-size: 1.3rem; margin-bottom: 1.5rem; }
  h2 {
    font-size: 1rem;
    font-weight: 600;
    color: #444;
    margin: 1.8rem 0 0.8rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid #e5e7eb;
  }
  label {
    display: block;
    font-size: 0.88rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.3rem;
  }
  .field { margin-bottom: 1.2rem; }
  .number-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
  }
  input[type="password"],
  input[type="number"] {
    width: 100%;
    padding: 0.55rem 0.75rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
  }
  input[type="number"] { font-size: 0.95rem; }
  .categories {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem 1.5rem;
  }
  .categories label {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-weight: 400;
    cursor: pointer;
  }
  input[type="checkbox"] {
    width: 1rem;
    height: 1rem;
    cursor: pointer;
  }
  textarea {
    width: 100%;
    padding: 0.6rem 0.75rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.82rem;
    resize: vertical;
  }
  .textarea-sm { height: 10rem; }
  .textarea-md { height: 16rem; }
  .textarea-lg { height: 26rem; }
  button {
    padding: 0.55rem 1.2rem;
    background: #2563eb;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.95rem;
  }
  button:hover { background: #1d4ed8; }
  .row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
  .actions {
    display: flex;
    gap: 1rem;
    align-items: center;
    margin-top: 1.4rem;
  }
  a { color: #2563eb; font-size: 0.9rem; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .err { color: #dc2626; font-size: 0.9rem; }
  .ok  { color: #16a34a; font-size: 0.9rem; }
</style>"""


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


def _page(title: str, body: str) -> str:
    return (
        "<!DOCTYPE html>\n"
        "<html lang='no'>\n"
        "<head>\n"
        "  <meta charset='utf-8'>\n"
        f"  <title>{title}</title>\n"
        + _STYLE + "\n"
        "</head>\n"
        "<body>\n"
        + body
        + "</body>\n"
        "</html>"
    )


def _disabled_page() -> HTMLResponse:
    body = (
        "<div class='card'>\n"
        "  <h1>OS-bot Admin</h1>\n"
        "  <p class='err'>\n"
        "    Admin-grensesnittet er deaktivert. "
        "Passordfil mangler eller er tom.\n"
        "    Se serverloggene.\n"
        "  </p>\n"
        "</div>\n"
    )
    return HTMLResponse(_page("OS-bot Admin", body), status_code=503)


def _login_page(error: str = "") -> HTMLResponse:
    err = f"    <p class='err'>{html.escape(error)}</p>\n" if error else ""
    body = (
        "<div class='card'>\n"
        "  <h1>OS-bot Admin</h1>\n"
        "  <form method='post' action='/admin/login'>\n"
        "    <input type='password' name='password' placeholder='Passord'\n"
        "           autofocus autocomplete='current-password'>\n"
        "    <button type='submit'>Logg inn</button>\n"
        + err
        + "  </form>\n"
        "</div>\n"
    )
    return HTMLResponse(_page("OS-bot Admin", body))


def _category_checkboxes(selected: list[str]) -> str:
    parts = []
    for cat in _ALL_CATEGORIES:
        checked = " checked" if cat in selected else ""
        parts.append(
            f"        <label>\n"
            f"          <input type='checkbox' name='socratic_categories'"
            f" value='{cat}'{checked}> {cat}\n"
            f"        </label>"
        )
    return "\n".join(parts)


def _textarea(name: str, size: str, value: str) -> str:
    safe = html.escape(value)
    return (
        f"    <div class='field'>\n"
        f"      <textarea id='{name}' name='{name}'\n"
        f"                class='textarea-{size}'\n"
        f"                spellcheck='false'>{safe}</textarea>\n"
        f"    </div>\n"
    )


def _settings_page(
    cfg: dict, message: str = "", is_error: bool = False
) -> HTMLResponse:
    msg = ""
    if message:
        cls = "err" if is_error else "ok"
        msg = f"      <span class='{cls}'>{html.escape(message)}</span>\n"

    checkboxes = _category_checkboxes(cfg.get("socratic_categories", []))
    temp = cfg.get("temperature", 0.2)
    rep = cfg.get("repetition_penalty", 1.1)
    maxt = cfg.get("max_tokens", 131072)

    body = (
        "<div class='wrap'>\n"
        "  <form method='post' action='/admin/settings'>\n"
        "    <div class='row'>\n"
        "      <h1>Innstillinger</h1>\n"
        "      <a href='/admin/logout'>Logg ut</a>\n"
        "    </div>\n"
        "\n"
        "    <h2>LLM-parametere</h2>\n"
        "    <div class='number-row'>\n"
        "      <div class='field'>\n"
        "        <label for='temperature'>Temperatur</label>\n"
        f"        <input type='number' id='temperature' name='temperature'\n"
        f"               step='0.01' min='0' max='2' value='{temp}'>\n"
        "      </div>\n"
        "      <div class='field'>\n"
        "        <label for='repetition_penalty'>Repetition penalty</label>\n"
        f"        <input type='number' id='repetition_penalty'\n"
        f"               name='repetition_penalty'\n"
        f"               step='0.01' min='1' max='3' value='{rep}'>\n"
        "      </div>\n"
        "      <div class='field'>\n"
        "        <label for='max_tokens'>Maks. tokens</label>\n"
        f"        <input type='number' id='max_tokens' name='max_tokens'\n"
        f"               step='1' min='1' value='{maxt}'>\n"
        "      </div>\n"
        "    </div>\n"
        "\n"
        "    <h2>Sokratisk modus</h2>\n"
        "    <div class='field'>\n"
        "      <label>Kategorier som utløser sokratisk modus</label>\n"
        "      <div class='categories'>\n"
        + checkboxes + "\n"
        "      </div>\n"
        "    </div>\n"
        "\n"
        "    <h2>Intent classifier-prompt</h2>\n"
        + _textarea(
            "intent_classifier_prompt", "md",
            cfg.get("intent_classifier_prompt", ""),
        )
        + "\n"
        "    <h2>Direkte modus – intro</h2>\n"
        + _textarea("direct_intro", "lg", cfg.get("direct_intro", ""))
        + "\n"
        "    <h2>Sokratisk modus – intro</h2>\n"
        + _textarea("socratic_intro", "lg", cfg.get("socratic_intro", ""))
        + "\n"
        "    <h2>Felles instruksjoner</h2>\n"
        + _textarea(
            "shared_instructions", "md",
            cfg.get("shared_instructions", ""),
        )
        + "\n"
        "    <div class='actions'>\n"
        "      <button type='submit'>Lagre</button>\n"
        + msg
        + "    </div>\n"
        "  </form>\n"
        "</div>\n"
    )
    return HTMLResponse(_page("OS-bot Admin – Innstillinger", body))


def _to_toml(
    temperature: float,
    repetition_penalty: float,
    max_tokens: int,
    intent_classifier_prompt: str,
    socratic_categories: list[str],
    direct_intro: str,
    socratic_intro: str,
    shared_instructions: str,
) -> str:
    def ml(s: str) -> str:
        s = s.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
        if "'''" not in s:
            return f"'''\n{s}\n'''"
        s = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"""\n{s}\n"""'

    cats = ", ".join(f'"{c}"' for c in socratic_categories)
    return "\n".join([
        f"temperature = {temperature}",
        f"repetition_penalty = {repetition_penalty}",
        f"max_tokens = {max_tokens}",
        "",
        f"intent_classifier_prompt = {ml(intent_classifier_prompt)}",
        "",
        f"socratic_categories = [{cats}]",
        "",
        f"direct_intro = {ml(direct_intro)}",
        "",
        f"socratic_intro = {ml(socratic_intro)}",
        "",
        f"shared_instructions = {ml(shared_instructions)}",
        "",
    ])


@router.get("/admin", response_class=HTMLResponse)
async def admin_get(session: str | None = Cookie(default=None)):
    if _PASSWORD is None:
        return _disabled_page()
    if not _is_authenticated(session):
        return RedirectResponse("/admin/login", status_code=302)
    return _settings_page(_settings.load())


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
    temperature: float = Form(...),
    repetition_penalty: float = Form(...),
    max_tokens: int = Form(...),
    intent_classifier_prompt: str = Form(...),
    socratic_categories: list[str] = Form(default=[]),
    direct_intro: str = Form(...),
    socratic_intro: str = Form(...),
    shared_instructions: str = Form(...),
    session: str | None = Cookie(default=None),
):
    if _PASSWORD is None:
        return _disabled_page()
    if not _is_authenticated(session):
        return RedirectResponse("/admin/login", status_code=302)

    cfg = {
        "temperature": temperature,
        "repetition_penalty": repetition_penalty,
        "max_tokens": max_tokens,
        "intent_classifier_prompt": intent_classifier_prompt,
        "socratic_categories": socratic_categories,
        "direct_intro": direct_intro,
        "socratic_intro": socratic_intro,
        "shared_instructions": shared_instructions,
    }
    content = _to_toml(**cfg)

    try:
        _settings.save(content)
    except tomllib.TOMLDecodeError as e:
        return _settings_page(cfg, f"Ugyldig TOML: {e}", is_error=True)
    except OSError as e:
        return _settings_page(cfg, f"Kunne ikke lagre: {e}", is_error=True)
    return _settings_page(cfg, "Innstillinger lagret.")
