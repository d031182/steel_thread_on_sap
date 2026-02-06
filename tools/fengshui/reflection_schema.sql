-- Reflection database for meta-learning
-- Location: tools/fengshui/reflection.db
-- Purpose: Track fix attempts and learn from execution patterns

CREATE TABLE IF NOT EXISTS fix_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    fix_type TEXT NOT NULL,
    module_name TEXT NOT NULL,
    strategy_used TEXT NOT NULL,
    predicted_success REAL NOT NULL,  -- 0.0-1.0
    actual_success INTEGER NOT NULL,   -- 0 or 1
    execution_time_ms INTEGER NOT NULL,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS strategy_performance (
    strategy_name TEXT PRIMARY KEY,
    total_attempts INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    avg_execution_time_ms REAL NOT NULL DEFAULT 0.0,
    trend TEXT NOT NULL DEFAULT 'STABLE',  -- IMPROVING/STABLE/DECLINING
    last_updated TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reflection_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    insight_type TEXT NOT NULL,
    priority TEXT NOT NULL,  -- CRITICAL/HIGH/MEDIUM/LOW
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN'  -- OPEN/ACKNOWLEDGED/RESOLVED
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_fix_attempts_timestamp ON fix_attempts(timestamp);
CREATE INDEX IF NOT EXISTS idx_fix_attempts_module ON fix_attempts(module_name);
CREATE INDEX IF NOT EXISTS idx_fix_attempts_strategy ON fix_attempts(strategy_used);
CREATE INDEX IF NOT EXISTS idx_insights_priority ON reflection_insights(priority);
CREATE INDEX IF NOT EXISTS idx_insights_status ON reflection_insights(status);