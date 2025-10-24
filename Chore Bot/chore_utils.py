from dateutil import parser as date_parser
from canvas_utils import TZ, CLIENT_STATE_DIR, load_json, save_json
from datetime import datetime, timedelta
import re
import os
import logs


log = logs.Logger("bot")

def parse_frequency(freq_str: str) -> dict:
    freq_str = freq_str.strip()

    date_patterns = [
        r'(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?',
        r'(\w+)\s+(\d{1,2})(?:,?\s+(\d{4}))?'
    ]

    for pattern in date_patterns:
        match = re.match(pattern, freq_str, re.IGNORECASE)
        if match:
            try:
                parsed_date = date_parser.parse(freq_str, fuzzy = True)
                now = datetime.now(TZ)

                if parsed_date.year == now.year and parsed_date < now:
                    parsed_date = parsed_date.replace(year = now.year + 1)

                if parsed_date.tzinfo is None:
                    parsed_date = parsed_date.replace(tzinfo = TZ)

                return {'type': 'one_type', 'date': parsed_date}
            except (ValueError, date_parser.ParserError) as e:
                log.error(f'Error when trying to parse date: {str(e)}')
                pass

    freq_lower = freq_str.lower()
    match = re.match(r'(\d+)\s*(day|days|week|weeks|month|months)', freq_lower)
    if not match:
        return None
    
    num = int(match.group(1))
    unit = match.group(2)

    if 'day' in unit:
        days = num
    elif 'week' in unit:
        days = num * 7
    elif 'month' in unit:
        days = num * 30
    else:
        return None
    
    return {'type': 'recurring', 'days': days}

def get_next_due_date(last_completed, frequency_days, localtz):
    if not last_completed:
        return datetime.now(localtz)
    return last_completed + timedelta(days = frequency_days)

def chore_state_path(guild_id: int) -> str:
    return os.path.join(CLIENT_STATE_DIR, f'chore_state_{guild_id}.json')

def load_chore_state(guild_id: int) -> dict:
    return load_json(chore_state_path(guild_id), {})

def save_chore_state(guild_id: int, state: dict):
    save_json(chore_state_path(guild_id), state)
