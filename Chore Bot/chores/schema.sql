PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS chore_lists(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    guild_id INTEGER,
    list_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, list_name)
); 

CREATE TABLE IF NOT EXISTS chores(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    chore_type TEXT NOT NULL CHECK(chore_type IN ('recurring', 'one_time')),
    assigned_to INTEGER NOT NULL,
    frequency_days INTEGER,
    due_date TIMESTAMP,
    last_completed TIMESTAMP,
    next_due TIMESTAMP,
    completed BOOLEAN DEFAULT 0,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (list_id) REFERENCES chore_lists(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reminder_state(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    chore_id INTEGER NOT NULL,
    reminder_type TEXT NOT NULL,
    reminded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(chore_id, reminder_type)
); 

CREATE INDEX IF NOT EXISTS idx_chores_list ON chores(list_id);
CREATE INDEX IF NOT EXISTS idx_chores_assigned ON chores(assigned_to);
CREATE INDEX IF NOT EXISTS idx_chores_type ON chores(chore_type);
CREATE INDEX IF NOT EXISTS idx_chores_completed ON chores(completed);
CREATE INDEX IF NOT EXISTS idx_chores_next_due ON chores(next_due);
CREATE INDEX IF NOT EXISTS idx_lists_user ON chore_lists(user_id);
CREATE INDEX IF NOT EXISTS idx_lists_guild ON chore_lists(guild_id);
CREATE INDEX IF NOT EXISTS idx_reminder_chore ON reminder_state(chore_id);

CREATE VIEW IF NOT EXISTS v_chores_with_lists AS
SELECT
    c.id,
    c.name AS chore_name,
    c.chore_type,
    c.assigned_to,
    c.frequency_days,
    c.due_date,
    c.next_due,
    c.last_completed,
    c.completed,
    cl.list_name,
    cl.user_id,
    cl.guild_id
FROM chores c
JOIN chore_lists cl ON c.list_id = cl.id;


CREATE VIEW IF NOT EXISTS v_overdue_chores AS
SELECT 
    c.id,
    c.name,
    c.chore_type,
    c.assigned_to,
    CASE
        WHEN c.chore_type = 'one_time' THEN c.due_date
        ELSE c.next_due
    END AS due_date,
    cl.list_name,
    cl.user_id,
    cl.guild_id
FROM chores c
JOIN chore_lists cl on cl.list_id = c.list_id
WHERE c.completed = 0
AND (
    (c.chore_type = 'one_time' AND datetime(c.due_date) < datetime('now'))
    OR
    (c.chore_type = 'recurring' AND datetime(c.next_due) < datetime('now'))
);