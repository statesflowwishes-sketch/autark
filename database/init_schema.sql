-- Erweiterte Audit & Metadaten Datenbank Schema
-- KI Agent Orchestrator System

-- Enable Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Audit Table (existing enhanced)
CREATE TABLE IF NOT EXISTS audits (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    task_id TEXT NOT NULL,
    state TEXT NOT NULL,
    previous_state TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT DEFAULT 'system',
    execution_time_ms INTEGER,
    cost_usd DECIMAL(10,4),
    error_details TEXT,
    INDEX (task_id),
    INDEX (state),
    INDEX (created_at)
);

-- Agent Sessions
CREATE TABLE IF NOT EXISTS agent_sessions (
    id SERIAL PRIMARY KEY,
    session_uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    agent_type TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    configuration JSONB DEFAULT '{}',
    metrics JSONB DEFAULT '{}',
    INDEX (agent_type),
    INDEX (status)
);

-- Task Execution History
CREATE TABLE IF NOT EXISTS task_executions (
    id SERIAL PRIMARY KEY,
    task_uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    goal TEXT NOT NULL,
    repo_url TEXT,
    branch TEXT DEFAULT 'main',
    mode TEXT CHECK (mode IN ('refactor', 'new_feature', 'bugfix', 'app_generation')),
    status TEXT DEFAULT 'pending',
    iterations_count INTEGER DEFAULT 0,
    max_iterations INTEGER DEFAULT 8,
    cost_budget_usd DECIMAL(10,4) DEFAULT 5.0,
    cost_spent_usd DECIMAL(10,4) DEFAULT 0.0,
    time_budget_minutes INTEGER DEFAULT 60,
    time_spent_minutes INTEGER DEFAULT 0,
    acceptance_criteria JSONB DEFAULT '[]',
    constraints JSONB DEFAULT '{}',
    results JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_by TEXT DEFAULT 'system',
    INDEX (status),
    INDEX (mode),
    INDEX (created_at)
);

-- Model Usage Tracking
CREATE TABLE IF NOT EXISTS model_usage (
    id SERIAL PRIMARY KEY,
    model_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    task_uuid UUID REFERENCES task_executions(task_uuid),
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,6) DEFAULT 0.0,
    latency_ms INTEGER,
    quality_score DECIMAL(3,2),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    INDEX (model_id),
    INDEX (provider),
    INDEX (timestamp)
);

-- Code Changes Tracking
CREATE TABLE IF NOT EXISTS code_changes (
    id SERIAL PRIMARY KEY,
    change_uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    task_uuid UUID REFERENCES task_executions(task_uuid),
    file_path TEXT NOT NULL,
    change_type TEXT CHECK (change_type IN ('created', 'modified', 'deleted', 'moved')),
    lines_added INTEGER DEFAULT 0,
    lines_removed INTEGER DEFAULT 0,
    diff_content TEXT,
    commit_hash TEXT,
    agent_responsible TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    INDEX (task_uuid),
    INDEX (change_type),
    INDEX (file_path)
);

-- Security Events
CREATE TABLE IF NOT EXISTS security_events (
    id SERIAL PRIMARY KEY,
    event_uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    event_type TEXT NOT NULL,
    severity TEXT CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    task_uuid UUID REFERENCES task_executions(task_uuid),
    description TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    INDEX (event_type),
    INDEX (severity),
    INDEX (resolved)
);

-- Performance Metrics
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    metric_name TEXT NOT NULL,
    metric_value DECIMAL(15,6),
    metric_unit TEXT,
    task_uuid UUID REFERENCES task_executions(task_uuid),
    agent_type TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    INDEX (metric_name),
    INDEX (timestamp),
    INDEX (agent_type)
);

-- System Configuration
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key TEXT UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    config_type TEXT DEFAULT 'general',
    is_encrypted BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT DEFAULT 'system',
    INDEX (config_key),
    INDEX (config_type)
);

-- Insert default configurations
INSERT INTO system_config (config_key, config_value, config_type) VALUES
('max_iterations_default', '8', 'execution'),
('cost_budget_default_usd', '5.0', 'cost'),
('time_budget_default_minutes', '60', 'execution'),
('secure_mode', 'true', 'security'),
('git_commit_signing', 'true', 'git'),
('embedding_strategy', '"semantic+symbol"', 'ai'),
('sandbox_tier_default', '"medium"', 'security')
ON CONFLICT (config_key) DO NOTHING;

-- Create Functions for automatic timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create Triggers
CREATE TRIGGER update_audits_updated_at BEFORE UPDATE ON audits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create Views for common queries
CREATE OR REPLACE VIEW active_tasks AS
SELECT 
    te.*,
    COUNT(cc.id) as code_changes_count,
    SUM(mu.cost_usd) as total_cost
FROM task_executions te
LEFT JOIN code_changes cc ON te.task_uuid = cc.task_uuid
LEFT JOIN model_usage mu ON te.task_uuid = mu.task_uuid
WHERE te.status IN ('pending', 'running', 'paused')
GROUP BY te.id;

CREATE OR REPLACE VIEW cost_summary AS
SELECT 
    DATE(timestamp) as date,
    provider,
    model_id,
    SUM(cost_usd) as daily_cost,
    COUNT(*) as usage_count,
    AVG(latency_ms) as avg_latency
FROM model_usage
GROUP BY DATE(timestamp), provider, model_id
ORDER BY date DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ki_agent;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ki_agent;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO ki_agent;