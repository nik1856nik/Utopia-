# Tests and deployment verification

The suite uses an in-memory SQLite database per test. It does not touch the development/host database. Five regression checks are marked `xfail`: four capture known authorization gaps and one captures the stormwater routing bug tracked in `ISSUE.md`. Pytest reports these as expected failures until the implementation is fixed.

## Run backend tests

From the repository root, install the test dependencies into an isolated environment and run the suite:

```sh
uv venv .venv-test --python 3.12
uv pip install --python .venv-test/bin/python -r test/requirements.txt
.venv-test/bin/python -m pytest test -q
```

Show line coverage and uncovered lines:

```sh
.venv-test/bin/python -m pytest test --cov=app --cov-report=term-missing
```

The HTTP tests exercise each registered API route, schemas and serialization, database compatibility helper, startup hook, seeding, geocoding, JWT handling, and DigSync. Coverage output is the source of truth for missed branches. The legacy `scratch/test_acceptance.py` requires a separately running API and refers to routes/status codes that no longer match the current app; use this isolated suite instead.

## Check frontend source/build

The frontend has no standalone component unit-test runner yet. Pytest runs a production build smoke test when `frontend/node_modules` exists. The build runs TypeScript's project checks and Vite bundling:

```sh
cd frontend
npm ci
npm run build
```

The Compose smoke test also verifies the built single-page app is served and that a client-side path receives the SPA fallback. That is an HTTP deployment check, not browser-level interaction coverage of every React component.

## Verify Compose and Nginx

Configuration checks are part of pytest (`test_deployment_config.py`). For a live smoke test, create the root `.env` as described in `ISSUE.md`, then:

```sh
docker compose -f compose.yml up --build -d
docker compose -f compose.yml ps
python test/compose_smoke.py
```

The script checks the root HTML, `/citizen` SPA fallback, Nginx proxying to `/api/health`, `/api/projects`, `/docs`, and `/openapi.json`, then writes a uniquely named project through the API.

To verify the PostgreSQL named volume survives a container restart, immediately after that smoke test run:

```sh
docker compose -f compose.yml restart db api
python test/compose_smoke.py --verify-persistence
```

Check container health and Nginx/API logs if anything fails:

```sh
docker compose -f compose.yml ps
docker compose -f compose.yml exec -T web nginx -t
docker compose -f compose.yml logs --tail=200 web api db
```

`web` should be running, `api` should report healthy, and `db` should report healthy. Nginx proxy failures commonly show as 502 in `web` logs; API startup/database failures appear in `api` logs. Stop the stack with `docker compose -f compose.yml down` (this retains `pgdata`).
