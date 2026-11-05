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

-- Populated by the Lambda demo (examples/run_lambda_architecture.py).
-- Three separate tables mirror the architecture's three layers: the batch
-- layer fully replaces lambda_batch_view on each (slow) run; the speed
-- layer fully replaces lambda_speed_view on each (fast, small-window) run;
-- the serving layer upserts the merged result into lambda_serving_view,
-- which is what a consumer should actually query.
CREATE TABLE IF NOT EXISTS lambda_batch_view (
    customer_id     INTEGER PRIMARY KEY,
    name            TEXT,
    email           TEXT,
    country         TEXT,
    order_count     INTEGER DEFAULT 0,
    total_spent     NUMERIC(10, 2) DEFAULT 0,
    last_order_date DATE
);

CREATE TABLE IF NOT EXISTS lambda_speed_view (
    customer_id     INTEGER PRIMARY KEY,
    name            TEXT,
    email           TEXT,
    country         TEXT,
    order_count     INTEGER DEFAULT 0,
    total_spent     NUMERIC(10, 2) DEFAULT 0,
    last_order_date DATE
);

CREATE TABLE IF NOT EXISTS lambda_serving_view (
    customer_id     INTEGER PRIMARY KEY,
    name            TEXT,
    email           TEXT,
    country         TEXT,
    order_count     INTEGER DEFAULT 0,
    total_spent     NUMERIC(10, 2) DEFAULT 0,
    last_order_date DATE
);

-- Populated by the Data Mesh demo (examples/run_data_mesh.py). Each
-- domain owns and publishes only its own table: the customers domain
-- never writes order activity, and the orders domain never writes
-- customer identity fields (see data_proc.data_mesh.domains). The
-- consumer view is produced by joining both products at read time, not by
-- either domain, demonstrating self-serve cross-domain composition.
CREATE TABLE IF NOT EXISTS data_mesh_customers_product (
    customer_id     INTEGER PRIMARY KEY,
    name            TEXT,
    email           TEXT,
    country         TEXT,
    signup_date     DATE,
    company         TEXT
);

CREATE TABLE IF NOT EXISTS data_mesh_orders_product (
    customer_id     INTEGER PRIMARY KEY,
    order_count     INTEGER DEFAULT 0,
    total_spent     NUMERIC(10, 2) DEFAULT 0,
    last_order_date DATE
);

CREATE TABLE IF NOT EXISTS data_mesh_consumer_view (
    customer_id     INTEGER PRIMARY KEY,
    name            TEXT,
    email           TEXT,
    country         TEXT,
    order_count     INTEGER DEFAULT 0,
    total_spent     NUMERIC(10, 2) DEFAULT 0,
    last_order_date DATE
);
