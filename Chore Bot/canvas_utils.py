from icalendar import Calendar
from datetime import datetime, timedelta
import pytz, requests, os
import json, hashlib, asyncio
from dateutil import tz
import feedparser
import logs
from bs4 import BeautifulSoup
import html
import re
from urllib.parse import urlparse , parse_qs

# --------------- Variable Configs ---------------
POLL_MIN = 10
LOOKAHEAD_DAYS = 15
TZ = tz.gettz('America/Los_Angeles')
ANNOUNCEMENTS = ""
log = logs.Logger("bot")
CLIENT_STATE_DIR = './Chore Bot/client_states'

# -------- Directory info --------
os.makedirs(CLIENT_STATE_DIR, exist_ok=True)
users_file = os.path.join(CLIENT_STATE_DIR, 'users.json')

# -------- File functions ---------
def load_json(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    except json.JSONDecodeError:
        return default
    
    except Exception:
        return default

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)

users = load_json(users_file, {})

def users_seen_path(uid: int) -> str:
    return os.path.join(CLIENT_STATE_DIR, f'ics_seen_{uid}.json')

def load_seen(uid: int) -> dict:
    return load_json(users_seen_path(uid), {})

def save_seen(uid: int, data: dict) -> bool:
    try:
        save_json(users_seen_path(uid), data)
        return True
    
    except Exception as e:
        log.error(f'Exception occurred when trying to save: {str(e)}')
        print('Exception occurred when trying to save file')
        return False


# ---------- Util functions ----------
def tz_for_user(uid: int):
    name = users.get(str(uid), {}).get('tz') or 'America/Los_Angeles'
    return tz.gettz(name)

def to_local(dtobj, localtz):
    if hasattr(dtobj, 'tzinfo'):
        if dtobj.tzinfo is None:
            from dateutil import tz as _tz
            dtobj = dtobj.replace(tzinfo = _tz.UTC)
        
        return dtobj.astimezone(localtz)
    return datetime(dtobj.year, dtobj.month, dtobj.day, tzinfo=localtz)

def event_start(comp, localtz):
    for key in ('DTSTART', 'DUE'):
        v = comp.get(key)
        if v and hasattr(v, 'dt'):
            return to_local(v.dt, localtz)
    
    return None

def event_url(comp):
    return str(comp.get('URL') or "")

def looks_like_assignment(summary, desc, url):
    s = (summary or "").lower()
    d = (desc or "").lower()
    u = (url or "").lower()

    keywords = ("due", "assignment", "quiz", "homework", "lab", "project", "exam", "checkpoint", "milestone")
    return any(k in s for k in keywords) or any(k in d for k in keywords) or ('/assignments/' in u) or ('/quizzes/' in u)

def event_fingerprint(comp, localtz):
    parts = []
    for key in ('SUMMARY', 'DESCRIPTION', 'LOCATION', 'SEQUENCE', 'STATUS'):
        val = comp.get(key)
        parts.append(str(val) if val is not None else "")

    for key in ('DTSTART', 'DTEND', 'DUE'):
        v = comp.get(key)
        if v and hasattr(v, 'dt'):
            parts.append(to_local(v.dt, localtz=localtz).isoformat())

        else:
            parts.append("")
    
    parts.append(event_url(comp=comp))
    return hashlib.sha256("|".join(parts).encode('utf-8')).hexdigest()[:16]

def event_uid(comp, start_iso: str) -> str:
    uid = str(comp.get('UID') or '').strip()

    if uid:
        return uid
    
    summary = str(comp.get('SUMMARY') or '').strip()
    fallback = hashlib.sha256((summary + '|' + start_iso).encode('utf-8')).hexdigest()[:16]
    return f'fb-{fallback}'


# ------- Format functions -------

def chunk(text, limit=2000):
    out, cur = [], ""

    for line in text.splitlines(True):
        if len(cur) + len(line) > limit:
            out.append(cur)
            cur = ""
        cur += line
    
    if cur:
        out.append(cur)
    
    return out

def fmt_due_line(title, when, url=""):
    when_str = when.strftime("%a %b %d %I:%M %p %Z")
    line = f"• **{title}**\n  When: {when_str}"

    if url:
        line += f'\n Link: {url}'
    return line

def parse_ics(text: bytes) -> Calendar:
    return Calendar.from_ical(text)

# ------- HTML -------
def event_description(comp) -> str:
    raw = None

    if comp.get('DESCRIPTION')is not None:
        raw = str(comp.get('DESCRIPTION'))
    
    elif comp.get('X-ALT-DESC') is not None:
        raw = str(comp.get('X-ALT-DESC'))

    else:
        return ""
    text = ""
    unescaped = html.unescape(raw).replace("\xa0", " ")
    if "<" in unescaped and ">" in unescaped:
        soup = BeautifulSoup(unescaped, 'html.parser')
        text = soup.get_text(separator="\n", strip=True)

    else:
        text = unescaped

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text

course_re = re.compile(r"course_(\d+)")
assign_re = re.compile(r"assignment_(\d+)")

def build_url(calendar_url: str) -> str | None:
    if not calendar_url:
        return None
    
    try:
        u = urlparse(calendar_url)
        q = parse_qs(u.query)
        course_id = None
        for vals in q.values():
            for val in vals:
                m = course_re.search(val)
                if m:
                    course_id = m.group(1)
                    break
            if course_id:
                break
        
        if not course_id:
            m = course_re.search(calendar_url)
            if m:
                course_id = m.group(1)

        assignment_id = None
        if u.fragment:
            m = assign_re.search(u.fragment)
            if m:
                assignment_id = m.group(1)
        
        if course_id and assignment_id:
            return f"{u.scheme}://{u.netloc}/courses/{course_id}/assignments/{assignment_id}"
        
    except Exception:
        pass
    return None

# ------- Miscellaneous --------
def get_user_ics(uid: int) -> str | None:
    return (users.get(str(uid)) or {}).get('ics_link')

def set_user_ics(uid: int, url: str):
    entry = users.get(str(uid), {})
    entry['ics_link'] = url.strip()
    entry.setdefault('tz', 'America/Los Angeles')
    users[str(uid)] = entry
    save_json(users_file, users)

def reminder_state_path(uid: int) -> str:
    return os.path.join(CLIENT_STATE_DIR, f'{uid}-reminds.json')

def load_reminded(uid: int) -> dict:
    return load_json(reminder_state_path(uid), {})

def save_reminded(uid: int, state: dict):
    save_json(reminder_state_path(uid), state)

def remind_alert(now_local: datetime, due_local: datetime) -> bool:
    return now_local < due_local <= now_local + timedelta(days=1)

