-- Run this in pgAdmin Query Tool while connected as a PostgreSQL superuser.
-- pgAdmin does not use psql commands like \connect, so run this in two steps.

-- Step 1: Connect to the default `postgres` database, then run:
CREATE DATABASE aiot_db;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_catalog.pg_roles WHERE rolname = 'aiot_user'
    ) THEN
        CREATE USER aiot_user WITH PASSWORD '123';
    END IF;
END
$$;

ALTER USER aiot_user WITH PASSWORD '123';

-- Step 2: In pgAdmin, switch/connect to the `aiot_db` database, then run:
GRANT ALL PRIVILEGES ON DATABASE aiot_db TO aiot_user;
GRANT ALL ON SCHEMA public TO aiot_user;
ALTER SCHEMA public OWNER TO aiot_user;
