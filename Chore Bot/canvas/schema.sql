PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY,
    ics_link TEXT,
    timezone TEXT DEFAULT 'America/Los Angeles',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 

CREATE TABLE IF NOT EXISTS assignment_reminders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event_id TEXT NOT NULL,
    reminder_type TEXT NOT NULL,
    fingerprint TEXT,
    reminded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, event_id ,reminder_type)
);

CREATE TABLE IF NOT EXISTS assignment_cache(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    user_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    title TEXT,
    due_date TIMESTAMP,
    url TEXT,
    description TEXT,
    fingerprint TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, event_id)
);

CREATE INDEX IF NOT EXISTS idx_reminders_user ON assignment_reminders(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_event ON assignment_reminders(event_id);
CREATE INDEX IF NOT EXISTS idx_cache_user ON assignment_cache(user_id);
CREATE INDEX IF NOT EXISTS idx_cache_due ON assignment_cache(due_date);
CREATE INDEX IF NOT EXISTS idx_cache_event ON assignment_cache(event_id);

CREATE VIEW IF NOT EXISTS v_users_with_ics AS
SELECT
    user_id, 
    ics_link,
    timezone,
    created_at
FROM user_settings
WHERE ics_link IS NOT NULL;

CREATE VIEW IF NOT EXISTS v_recent_reminders AS
SELECT
    ar.user_id,
    ar.event_id,
    ar.reminder_type,
    ar.reminded_at,
    ac.title,
    ac.due_date
FROM assignment_reminders ar
LEFT JOIN assignment_cache ac ON ar.user_id = ac.user_id AND ar.event_id = ac.event_id
WHERE ar.reminded_at > datetime('now', '-7 days')
ORDER BY ar.reminded_at DESC