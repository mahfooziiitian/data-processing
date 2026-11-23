---
diataxis: how-to
---

# Run the demos in Docker

Use the optional Compose app service to run the existing scripts in a
non-root container. Docker Compose builds the image and starts the local
PostgreSQL service when needed. The image includes the sample CSVs; no
local Python environment is required.
Run the commands from the repository root. `--project-directory .` keeps
Compose's project name, volume names, paths, and `.env` rooted there.

1. From the repository root, build the image and run batch ETL:

   ```bash
   docker compose --project-directory . -f infra/docker-compose.yml --profile tools build app
   docker compose --project-directory . -f infra/docker-compose.yml --profile tools run --rm app
   ```

   The batch run refreshes the demo database tables. It may contact the
   public enrichment API; an unreachable API is handled by the pipeline.
   The default database credentials are for local use only.

2. Run the other demos as needed:

   ```bash
   docker compose --project-directory . -f infra/docker-compose.yml --profile tools run --rm app examples/run_kappa_stream.py --seed
   docker compose --project-directory . -f infra/docker-compose.yml --profile tools run --rm app examples/run_kappa_stream.py --replay
   docker compose --project-directory . -f infra/docker-compose.yml --profile tools run --rm app examples/run_lambda_architecture.py --batch
   docker compose --project-directory . -f infra/docker-compose.yml --profile tools run --rm app examples/run_data_mesh.py
   ```

   Kappa seeding appends events each time. Replay resets the Kappa
   checkpoint and state and rebuilds its summary from the retained log.
   Lambda's batch run replaces its batch and speed views. Data Mesh
   publishing replaces its product tables and catalog entries.

3. Inspect the database or stop the services:

   ```bash
   docker compose --project-directory . -f infra/docker-compose.yml exec postgres psql -U postgres -d data_processing_demo \
     -c "SELECT * FROM customer_order_summary ORDER BY total_spent DESC;"
   docker compose --project-directory . -f infra/docker-compose.yml down
   ```

   The `pg_data` and `demo_state` named volumes survive `down`. The
   container's event logs, checkpoints, and catalog live in `demo_state`,
   separate from the host's `data/processed/`. Removing either volume
   destroys its stored data.

The app's `DATABASE_URL` defaults to the Compose PostgreSQL service. Set
`CONTAINER_DATABASE_URL` before invoking Compose to override it; `localhost`
inside the app container refers to that container, not the host. The
sample CSVs are baked into the image; rebuild after changing them.

This image is a local demo packaging option, not a production deployment.
The file-backed event state and catalog do not support coordinated
concurrent workers. Amazon MSK, AWS deployment, and Databricks execution
are not integrated; see [operational considerations](../explanation/operating-and-evolving.md).
