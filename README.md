# CTX OData Explorer

A lightweight application to inspect and test **only the `bdcdata-catalyst` CTX tables and schemas** from a SAP CAPM OData API.

- **Backend:** FastAPI + Python (Swagger UI at `/docs`)
- **Frontend:** React + TypeScript + Vite
- **Data sources:** Seed mode (local JSON fixtures) or OData mode (SAP CAPM service)
- **Scope:** Strictly limited to the approved CTX allowlist (16 entity sets)

## Repository layout

```
testctx/
├── backend/
│   ├── .env                # runtime config (gitignored, never commit credentials)
│   ├── .env.example        # placeholders only
│   ├── .gitignore
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # uvicorn entrypoint
│   │   ├── api/
│   │   │   └── routes.py           # FastAPI endpoints
│   │   ├── configuration/
│   │   │   └── settings.py         # pydantic-settings (.env)
│   │   ├── core/
│   │   │   ├── allowlist.py        # CTX allowlist (16 entities)
│   │   │   └── exceptions.py       # domain errors
│   │   ├── domain/
│   │   │   ├── entities.py         # CTX metadata (columns, keys, types)
│   │   │   └── schemas.py          # Pydantic API schemas
│   │   ├── persistence/
│   │   │   ├── base.py             # CTXRepository ABC
│   │   │   └── seed_repo.py        # JSON seed-data repository
│   │   └── services/
│   │       ├── ctx_service.py      # application service (+ import validation)
│   │       └── odata_service.py    # SAP CAPM OData client
│   ├── database/
│   │   └── ctx/
│   │       ├── metadata.json
│   │       └── seed_data/          # one JSON file per CTX entity
│   └── tests/
│       ├── conftest.py
│       ├── test_ctx.py
│       └── test_allowlist.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        ├── vite-env.d.ts
        ├── api/client.ts           # axios API client
        ├── types/index.ts
        ├── components/             # Sidebar, MetadataPanel, TryItPanel,
        │   ├── DataTable, ResponsePanel, SourceSelector, ImportSection
        └── pages/
```

## Strict CTX allowlist

Only these 16 entity sets are exposed (verified against the supplied metadata):

`CTX_RULEBOOK`, `CTX_MOVEMENT_CLASS`, `CTX_KPI_SOURCE_MAP`,
`CTX_KPI_CATALOG_MVT_TYPE`, `CTX_CDS_S4_TABLE_FIELD_MAP`, `CTX_KPI_CATALOG`,
`CTX_OBJECT_GRAIN_REGISTRY`, `CTX_RELATIONSHIP_REGISTRY`,
`CTX_KPI_RELATIONSHIP_USAGE`, `CTX_HARMONIZATION_RULES`,
`CTX_KPI_DEPENDENCY_GRAPH`, `CTX_PARAMETER_CONFIG`, `CTX_KPI_SAP_DETAIL`,
`CTX_MVP_SCOPE`, `CTX_REQUIREMENT_CATALOG`, `CTX_KNOWLEDGE_LINK`

Non-CTX entities such as `CsnDesignRun`, `ModelDesignRun`, `ProjectPortfolioView`
are rejected with `403`. There are no generic proxy endpoints for arbitrary entity
set access.

## Configuration (`.env`)

Copy `backend/.env.example` to `backend/.env` and adjust:

```
CTX_DATA_SOURCE=seed
CAPM_ODATA_BASE_URL=
CAPM_ODATA_USERNAME=
CAPM_ODATA_PASSWORD=
CORS_ORIGINS=http://localhost:5173
CTX_SEED_DATA_DIR=database/ctx/seed_data
```

- `CTX_DATA_SOURCE=seed` — load fixtures from `backend/database/ctx/seed_data/`. Works offline with no SAP BTP access.
- `CTX_DATA_SOURCE=odata` — fetch records from the configured SAP CAPM OData service (requires `CAPM_ODATA_BASE_URL`, credentials).
- Never commit real credentials; `.env` is gitignored and `.env.example` contains placeholders only.

## Backend setup

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Seed mode (offline, works immediately)
CTX_DATA_SOURCE=seed .venv/bin/uvicorn app.api.routes:app --reload --port 8000

# Or using .env
.venv/bin/uvicorn app.api.routes:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

## Frontend setup

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
npm run build      # production build
```

The Vite dev server proxies `/api` to `http://localhost:8000`.

## Backend API examples

List approved CTX entity sets:
```bash
curl http://localhost:8000/api/ctx/entities
```

Entity metadata (columns, key, namespace):
```bash
curl http://localhost:8000/api/ctx/entities/CTX_RULEBOOK/metadata
```

Fetch records (pagination + OData query params):
```bash
curl "http://localhost:8000/api/ctx/entities/CTX_MOVEMENT_CLASS/records?\$top=5"
curl "http://localhost:8000/api/ctx/entities/CTX_MOVEMENT_CLASS/records?\$top=1&\$skip=1"
curl "http://localhost:8000/api/ctx/entities/CTX_MOVEMENT_CLASS/records?\$filter=STATUS eq 'Active'"
```

Connection status:
```bash
curl http://localhost:8000/api/ctx/status
```

Validate imported metadata:
```bash
curl -X POST http://localhost:8000/api/ctx/import/metadata \
  -H 'Content-Type: application/json' \
  -d '{"content":"EntityType Name=\"CTX_RULEBOOK\" ..."}'
```

Import a metadata file (.xml/.json/.txt/.csn/.edmx, max 5 MB):
```bash
curl -X POST http://localhost:8000/api/ctx/import/metadata/file \
  -F "file=@metadata.xml"
```

Disallowed entity (403):
```bash
curl -i http://localhost:8000/api/ctx/entities/CsnDesignRun/records
```

## Tests

```bash
cd backend
.venv/bin/pytest -v
# 14 passed
```

## CORS

CORS is configured for the local frontend origin (`http://localhost:5173`) via `CORS_ORIGINS`. Credentials are allowed. Preflight `OPTIONS` returns `200` with `Access-Control-Allow-Origin` reflected.

**Browser CORS vs backend-to-OData:** Browser-enforced CORS applies only to requests made from a browser (e.g. the React frontend). The backend's calls to the SAP CAPM OData service are server-side HTTP requests and are **not** subject to browser CORS. Postman/Swagger UI requests made from the backend also do not prove browser CORS works. The `Access-Control-Allow-Origin` header on backend responses (verified above) is what enables browser access.

## Data sources & seed mode

Seed mode loads CTX-only JSON fixtures from `backend/database/ctx/seed_data/` (one file per entity). It is treated like a database-backed repository via the `CTXRepository` abstraction — no data is hardcoded in route handlers. Seed mode requires no SAP BTP credentials.

In OData mode, failure to reach the SAP service is reported clearly as an error; seed data is **never** silently substituted.

## What works / what was tested

- 14 pytest tests pass (entities, metadata, records, pagination, filter, status, import validation, allowlist, 403 for forbidden entities).
- Manual curl verification: root, entities list (16), metadata, paginated records, filter, connection status, 403 on `CsnDesignRun`, CORS preflight (200), CORS `Access-Control-Allow-Origin` reflection, `/docs` (200), import metadata validation.
- Frontend builds successfully with `npm run build` (TypeScript + Vite).

## Requires real SAP credentials / configuration

- OData mode requires a valid `CAPM_ODATA_BASE_URL`, `CAPM_ODATA_USERNAME`, and `CAPM_ODATA_PASSWORD` for a SAP CAPM service exposing the CTX entity sets.
- Backend-to-OData connectivity, authentication, and HTTP error handling are implemented but can only be fully validated against a real SAP BTP system.
- Direct browser access to the OData service's own CORS behavior depends on the SAP service configuration (not controlled by this app).
