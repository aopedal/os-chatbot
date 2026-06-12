import html
import logging
import os
import secrets
import time
import tomllib
from collections import defaultdict
from pathlib import Path
from typing import TypedDict, cast

import settings as _settings
from fastapi import APIRouter, Cookie, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

logger = logging.getLogger("server.admin")
router = APIRouter()


class Category(TypedDict):
    name: str
    description: str
    socratic: bool


class SettingsCfg(TypedDict):
    temperature: float
    repetition_penalty: float
    max_tokens: int
    intent_classifier_prompt: str
    categories: list[Category]
    direct_intro: str
    socratic_intro: str
    shared_instructions: str

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
  input[type="checkbox"] {
    width: 1rem;
    height: 1rem;
    cursor: pointer;
    flex-shrink: 0;
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
  .cat-list {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: 0.6rem;
  }
  .cat-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .cat-row input[type="text"] {
    padding: 0.4rem 0.6rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 0.88rem;
    font-family: monospace;
  }
  .cat-name { width: 13rem; }
  .cat-desc { flex: 1; }
  .btn-remove {
    padding: 0.3rem 0.55rem;
    background: #dc2626;
    font-size: 0.82rem;
    line-height: 1;
  }
  .btn-remove:hover { background: #b91c1c; }
  .btn-add {
    padding: 0.4rem 0.9rem;
    background: #16a34a;
    font-size: 0.88rem;
  }
  .btn-add:hover { background: #15803d; }
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
    return f"""\
<!DOCTYPE html>
<html lang='no'>
<head>
  <meta charset='utf-8'>
  <title>{title}</title>
{_STYLE}
</head>
<body>
{body}
</body>
</html>"""


def _disabled_page() -> HTMLResponse:
    body = """\
<div class='card'>
  <h1>OS-bot Admin</h1>
  <p class='err'>
    Admin-grensesnittet er deaktivert. Passordfil mangler eller er tom.
    Se serverloggene.
  </p>
</div>"""
    return HTMLResponse(_page("OS-bot Admin", body), status_code=503)


def _login_page(error: str = "") -> HTMLResponse:
    err = f"    <p class='err'>{html.escape(error)}</p>\n" if error else ""
    body = f"""\
<div class='card'>
  <h1>OS-bot Admin</h1>
  <form method='post' action='/admin/login'>
    <input type='password' name='password' placeholder='Passord'
           autofocus autocomplete='current-password'>
    <button type='submit'>Logg inn</button>
{err}  </form>
</div>"""
    return HTMLResponse(_page("OS-bot Admin", body))


def _category_rows(categories: list[Category]) -> str:
    rows: list[str] = []
    for i, cat in enumerate(categories):
        name = html.escape(cat.get("name", ""))
        desc = html.escape(cat.get("description", ""))
        checked = " checked" if cat.get("socratic", False) else ""
        rows.append(f"""\
            <div class='cat-row' data-index='{i}'>
                <input type='checkbox' name='category_socratic'
                       value='{i}'{checked}>
                <input type='text' name='category_name'
                       class='cat-name' value='{name}'
                       placeholder='CATEGORY_NAME'>
                <input type='text' name='category_description'
                       class='cat-desc' value='{desc}'
                       placeholder='Kort beskrivelse'>
                <button type='button' class='btn-remove'
                        onclick='removeCategory(this)'>×</button>
            </div>\
        """)
    return "\n".join(rows)


def _textarea(name: str, size: str, value: str) -> str:
    safe = html.escape(value)
    return f"""\
    <div class='field'>
      <textarea id='{name}' name='{name}'
                class='textarea-{size}'
                spellcheck='false'>{safe}</textarea>
    </div>"""


def _settings_page(
    cfg: SettingsCfg,
    message: str = "",
    is_error: bool = False,
) -> HTMLResponse:
    msg = ""
    if message:
        cls = "err" if is_error else "ok"
        msg = f"      <span class='{cls}'>{html.escape(message)}</span>\n"

    cat_rows = _category_rows(cfg.get("categories", []))
    temp = cfg.get("temperature", 0.2)
    rep = cfg.get("repetition_penalty", 1.1)
    maxt = cfg.get("max_tokens", 131072)
    ta_intent = _textarea(
        "intent_classifier_prompt",
        "md",
        cfg.get("intent_classifier_prompt", ""),
    )
    ta_direct = _textarea("direct_intro", "lg", cfg.get("direct_intro", ""))
    ta_socratic = _textarea("socratic_intro", "lg", cfg.get("socratic_intro", ""))
    ta_shared = _textarea(
        "shared_instructions",
        "md",
        cfg.get("shared_instructions", ""),
    )

    body = f"""\
<div class='wrap'>
  <form method='post' action='/admin/settings'>
    <div class='row'>
      <h1>Innstillinger</h1>
      <a href='/admin/logout'>Logg ut</a>
    </div>

    <h2>LLM-parametere</h2>
    <div class='number-row'>
      <div class='field'>
        <label for='temperature'>Temperatur</label>
        <input type='number' id='temperature' name='temperature'
               step='0.01' min='0' max='2' value='{temp}'>
      </div>
      <div class='field'>
        <label for='repetition_penalty'>Repetition penalty</label>
        <input type='number' id='repetition_penalty' name='repetition_penalty'
               step='0.01' min='1' max='3' value='{rep}'>
      </div>
      <div class='field'>
        <label for='max_tokens'>Maks. tokens</label>
        <input type='number' id='max_tokens' name='max_tokens'
               step='1' min='1' value='{maxt}'>
      </div>
    </div>

    <h2>Kategorier</h2>
    <div class='field'>
      <label>
        Hak av kategorier som utløser pedagogisk modus.
        Navn og beskrivelse brukes til å generere intent-prompten.
      </label>
      <div id='cat-list' class='cat-list'>
{cat_rows}
      </div>
      <button type='button' class='btn-add' onclick='addCategory()'>
        + Legg til kategori
      </button>
    </div>

    <h2>Intent classifier-prompt</h2>
    <div class='field'>
      <label>
        Bruk <code>{{categories}}</code> der kategorilistingen skal stå,
        og <code>{{question}}</code> for studentens spørsmål.
      </label>
    </div>
{ta_intent}

    <h2>Direkte modus – intro</h2>
{ta_direct}

    <h2>Pedagogisk modus – intro</h2>
{ta_socratic}

    <h2>Felles instruksjoner</h2>
{ta_shared}

    <div class='actions'>
      <button type='submit'>Lagre</button>
{msg}    </div>
  </form>
</div>
<script>
  function removeCategory(btn) {{
    btn.closest('.cat-row').remove();
    renumberCategories();
  }}

  function renumberCategories() {{
    document.querySelectorAll('.cat-row').forEach(function(row, i) {{
      row.dataset.index = i;
      row.querySelector('[name="category_socratic"]').value = i;
    }});
  }}

  function addCategory() {{
    var rows = document.querySelectorAll('.cat-row');
    var i = rows.length;
    var div = document.createElement('div');
    div.className = 'cat-row';
    div.dataset.index = i;
    div.innerHTML =
      '<input type="checkbox" name="category_socratic" value="' + i + '">'
      + '<input type="text" name="category_name" class="cat-name"'
      + ' placeholder="CATEGORY_NAME">'
      + '<input type="text" name="category_description" class="cat-desc"'
      + ' placeholder="Kort beskrivelse">'
      + '<button type="button" class="btn-remove"'
      + ' onclick="removeCategory(this)">&#xd7;</button>';
    document.getElementById('cat-list').appendChild(div);
  }}
</script>"""
    return HTMLResponse(_page("OS-bot Admin – Innstillinger", body))


def _to_toml(cfg: SettingsCfg) -> str:
    def ml(s: str) -> str:
        s = s.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
        if "'''" not in s:
            return f"'''\n{s}\n'''"
        s = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"""\n{s}\n"""'

    def cat_block(cat: Category) -> str:
        name = cat["name"].replace("\\", "\\\\").replace('"', '\\"')
        desc = cat["description"].replace("\\", "\\\\").replace('"', '\\"')
        socratic = "true" if cat["socratic"] else "false"
        return (
            "[[categories]]\n"
            f'name = "{name}"\n'
            f'description = "{desc}"\n'
            f"socratic = {socratic}"
        )

    parts = [
        f"temperature = {cfg['temperature']}",
        f"repetition_penalty = {cfg['repetition_penalty']}",
        f"max_tokens = {cfg['max_tokens']}",
        "",
        f"intent_classifier_prompt = {ml(cfg['intent_classifier_prompt'])}",
        "",
        f"direct_intro = {ml(cfg['direct_intro'])}",
        "",
        f"socratic_intro = {ml(cfg['socratic_intro'])}",
        "",
        f"shared_instructions = {ml(cfg['shared_instructions'])}",
    ]
    if cfg["categories"]:
        parts.append("")
        for cat in cfg["categories"]:
            parts.append(cat_block(cat))
            parts.append("")
    else:
        parts.append("")
    return "\n".join(parts)


@router.get("/admin", response_class=HTMLResponse)
async def admin_get(session: str | None = Cookie(default=None)):
    if _PASSWORD is None:
        return _disabled_page()
    if not _is_authenticated(session):
        return RedirectResponse("/admin/login", status_code=302)
    return _settings_page(cast(SettingsCfg, cast(object, _settings.load())))


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
    category_name: list[str] = Form(default=[]),
    category_description: list[str] = Form(default=[]),
    category_socratic: list[str] = Form(default=[]),
    direct_intro: str = Form(...),
    socratic_intro: str = Form(...),
    shared_instructions: str = Form(...),
    session: str | None = Cookie(default=None),
):
    if _PASSWORD is None:
        return _disabled_page()
    if not _is_authenticated(session):
        return RedirectResponse("/admin/login", status_code=302)

    checked = set(category_socratic)
    categories: list[Category] = [
        Category(
            name=name.strip(),
            description=desc.strip(),
            socratic=str(i) in checked,
        )
        for i, (name, desc) in enumerate(zip(category_name, category_description))
        if name.strip()
    ]

    cfg: SettingsCfg = {
        "temperature": temperature,
        "repetition_penalty": repetition_penalty,
        "max_tokens": max_tokens,
        "intent_classifier_prompt": intent_classifier_prompt,
        "categories": categories,
        "direct_intro": direct_intro,
        "socratic_intro": socratic_intro,
        "shared_instructions": shared_instructions,
    }
    content = _to_toml(cfg)

    try:
        _settings.save(content)
    except tomllib.TOMLDecodeError as e:
        return _settings_page(cfg, f"Ugyldig TOML: {e}", is_error=True)
    except OSError as e:
        return _settings_page(cfg, f"Kunne ikke lagre: {e}", is_error=True)
    return _settings_page(cfg, "Innstillinger lagret.")
