-- EveCalcDB initial schema for Cloud SQL (PostgreSQL 16)
-- Collation/encoding are set at DB creation (en_US.UTF8 / UTF8)

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_preferences (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  key VARCHAR(128) NOT NULL,
  value TEXT NOT NULL,
  CONSTRAINT uq_user_pref UNIQUE(user_id, key)
);

CREATE TABLE IF NOT EXISTS prices (
  id SERIAL PRIMARY KEY,
  resource VARCHAR(128) NOT NULL UNIQUE,
  price DOUBLE PRECISION NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS price_history (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  resource VARCHAR(128) NOT NULL,
  price_buy DOUBLE PRECISION,
  price_sell DOUBLE PRECISION,
  price_avg DOUBLE PRECISION,
  date TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_price_history_date ON price_history(date);
CREATE INDEX IF NOT EXISTS ix_price_history_resource ON price_history(resource);

CREATE TABLE IF NOT EXISTS mining_units (
  id SERIAL PRIMARY KEY,
  resource_key VARCHAR(128) NOT NULL UNIQUE,
  units INTEGER NOT NULL DEFAULT 0
);

-- Optional seed example (uncomment to prefill a couple of resources)
-- INSERT INTO prices(resource, price) VALUES
--   ('Base Metals', 10),
--   ('Heavy Metals', 25)
-- ON CONFLICT (resource) DO UPDATE SET price = EXCLUDED.price;


