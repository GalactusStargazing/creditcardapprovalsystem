-- Runs automatically on first container start via
-- /docker-entrypoint-initdb.d/ (official postgres image behavior)
-- Note: auth_db is already created automatically via POSTGRES_DB env var

CREATE DATABASE application_db;
CREATE DATABASE decision_db;
