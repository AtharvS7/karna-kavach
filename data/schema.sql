-- Karna Kavach Database Schema
-- Run via: psql -U postgres -d karna_kavach -f schema.sql

CREATE TABLE IF NOT EXISTS attacks (
    id               SERIAL PRIMARY KEY,
    attack_id        VARCHAR(100) UNIQUE NOT NULL,
    name             VARCHAR(255) NOT NULL,
    category         VARCHAR(100) NOT NULL,
    genai_amplification TEXT NOT NULL,
    attack_steps     JSONB NOT NULL DEFAULT '[]',
    target_channel   VARCHAR(100) NOT NULL,
    detection_challenges JSONB NOT NULL DEFAULT '[]',
    transaction_features JSONB NOT NULL DEFAULT '{}',
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS transactions (
    id               SERIAL PRIMARY KEY,
    transaction_id   VARCHAR(100) UNIQUE NOT NULL,
    card_id          VARCHAR(100) NOT NULL,
    merchant_name    VARCHAR(255) NOT NULL,
    merchant_category VARCHAR(100) NOT NULL,
    mcc              INTEGER,
    amount           NUMERIC(12,2) NOT NULL,
    currency         CHAR(3) DEFAULT 'USD',
    timestamp        TIMESTAMPTZ NOT NULL,
    city             VARCHAR(100) NOT NULL,
    state            VARCHAR(50),
    country          CHAR(2) NOT NULL DEFAULT 'US',
    card_present     BOOLEAN DEFAULT TRUE,
    is_fraud         BOOLEAN NOT NULL DEFAULT FALSE,
    attack_id        VARCHAR(100),
    fraud_probability NUMERIC(5,4),
    features         JSONB,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_metrics (
    id           SERIAL PRIMARY KEY,
    model_name   VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    metric_name  VARCHAR(100) NOT NULL,
    metric_value NUMERIC(8,6) NOT NULL,
    dataset_type VARCHAR(50) NOT NULL,
    iteration    INTEGER DEFAULT 0,
    metadata     JSONB,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_attacks_category  ON attacks(category);
CREATE INDEX IF NOT EXISTS idx_txn_card          ON transactions(card_id);
CREATE INDEX IF NOT EXISTS idx_txn_fraud         ON transactions(is_fraud);
CREATE INDEX IF NOT EXISTS idx_txn_timestamp     ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_model     ON model_metrics(model_name, model_version);
