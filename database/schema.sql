-- ============================================================
-- NEXUS-AI DISTRIBUTED GRID (NADG) - DATABASE SCHEMA
-- ============================================================
-- Purpose: Worker node registry and task tracking
-- Database: Supabase (PostgreSQL)
-- ============================================================

-- Worker Nodes Registry Table
CREATE TABLE worker_nodes (
    id SERIAL PRIMARY KEY,
    vm_url TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'active', -- active, busy, offline
    total_tasks INTEGER DEFAULT 0,
    last_ping TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX idx_worker_status ON worker_nodes(status);
CREATE INDEX idx_last_ping ON worker_nodes(last_ping);

-- Optional: Task History Table for tracking
CREATE TABLE task_history (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER REFERENCES worker_nodes(id),
    task_description TEXT,
    status TEXT DEFAULT 'pending', -- pending, running, completed, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);
