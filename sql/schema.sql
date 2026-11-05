-- Initial schema for the data-processing demo database.
-- Applied automatically by the postgres container on first startup
-- (mounted into /docker-entrypoint-initdb.d/).

CREATE TABLE IF NOT EXISTS customers (
    customer_id     INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    email           TEXT NOT NULL,
    country         TEXT,
    signup_date     DATE,
    company         TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    order_id        INTEGER PRIMARY KEY,
    customer_id     INTEGER REFERENCES customers (customer_id),
    product         TEXT NOT NULL,
    quantity        INTEGER NOT NULL,
    unit_price      NUMERIC(10, 2) NOT NULL,
    order_date      DATE,
    line_total      NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS customer_order_summary (
    customer_id     INTEGER PRIMARY KEY REFERENCES customers (customer_id),
    name            TEXT,
    email           TEXT,
    country         TEXT,
    signup_date     DATE,
    company         TEXT,
    order_count     INTEGER DEFAULT 0,
    total_spent     NUMERIC(10, 2) DEFAULT 0,
    last_order_date DATE
);

-- Populated by the Kappa demo (examples/run_kappa_stream.py), not the
-- batch pipeline. Deliberately a separate table from
-- customer_order_summary above: same analytical shape, but derived from
-- data_proc.kappa's event-log + replay path instead of CSV batch extracts,
-- to show both architectures can produce the same kind of output.
CREATE TABLE IF NOT EXISTS kappa_customer_order_summary (
    customer_id     INTEGER PRIMARY KEY,
    name            TEXT,
    email           TEXT,
    country         TEXT,
    order_count     INTEGER DEFAULT 0,
    total_spent     NUMERIC(10, 2) DEFAULT 0,
    last_order_date DATE
);
