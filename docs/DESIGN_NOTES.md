# Design & Planning Notes

Working notes on data model, API contract, seeding, validation, and folder structure.
These guide implementation; they are not final code.

## 1. Data model details

### Money representation

- Store monetary amounts as **integers** (e.g. whole base-currency units, or minor
units) to avoid floating-point rounding. Display formatting happens in the UI.
- Each amount is always paired with a **currency code** (ISO 4217, e.g. `USD`, `EUR`,
`INR`, `GBP`).

### Tables / entities

- **employee** — core record. Indexes on: `country`, `departmentId`, `level`, `status`,
and a search index on `lastName`/`email`/`employeeCode`.
- **compensation** — current pay for an employee (`baseAnnual`, `bonusAnnual`,
`currency`, `effectiveDate`, `isCurrent`). One current row per employee.
- **salary_change_history** — append-only audit (`field`, `oldValue`, `newValue`,
`changedBy`, `changedAt`, `note`).
- **department** — lookup (name).
- **fx_rate** — `currency` → `rateToUsd`, `asOf` (versioned; latest used for aggregates).
- **user** — HR Manager (`email`, `passwordHash`, `role`).

### Derived values (not stored)

- `monthlyBase = baseAnnual / 12`
- `totalComp = baseAnnual + bonusAnnual`
- `baseUsd = baseAnnual * fxRate(currency)`

## 2. API contract (draft)

> REST, JSON, JWT bearer auth on all `/employees`, `/analytics`, `/export` routes.


| Method | Path                          | Purpose                                                                     |
| ------ | ----------------------------- | --------------------------------------------------------------------------- |
| POST   | `/auth/login`                 | login → JWT                                                                 |
| GET    | `/employees`                  | list (query: `q, country, department, level, status, sort, page, pageSize`) |
| GET    | `/employees/:id`              | employee + current compensation                                             |
| POST   | `/employees`                  | create employee (+ initial compensation)                                    |
| PATCH  | `/employees/:id`              | update profile fields                                                       |
| PATCH  | `/employees/:id/compensation` | update base/bonus → writes history                                          |
| DELETE | `/employees/:id`              | soft-delete (status=inactive)                                               |
| GET    | `/employees/:id/history`      | salary change history                                                       |
| GET    | `/analytics/summary`          | org KPIs (respects filters)                                                 |
| GET    | `/analytics/breakdown`        | group by `country|department|level`                                         |
| GET    | `/export/employees.csv`       | CSV of filtered view                                                        |


### List response shape (paginated)

```json
{
  "data": [ { "id": "...", "name": "...", "country": "DE", "baseAnnual": 90000, "currency": "EUR", "baseUsd": 98000 } ],
  "page": 1,
  "pageSize": 25,
  "total": 10000
}
```

### Analytics summary shape

```json
{
  "headcount": 10000,
  "totalPayrollUsd": 925000000,
  "avgBaseUsd": 92500,
  "medianBaseUsd": 86000,
  "currencyBase": "USD",
  "fxAsOf": "2026-01-01"
}
```

## 3. Validation rules

- `baseAnnual` > 0 and within a sane band (e.g. 1k–10M base units) → reject outliers
with a clear message (guards against fat-finger Excel-style errors).
- `bonusAnnual` >= 0.
- `currency` required, must exist in `fx_rate`.
- `email` unique, valid format; `employeeCode` unique.
- Edits run in a **transaction** with the history insert (all-or-nothing).

## 4. Seeding (10,000 employees)

- Use **Python Faker** with a **fixed seed** (`Faker.seed(...)`) for reproducibility.
- Distribute realistically:
  - ~8–12 **countries** with matching **currencies** (US/USD, DE/EUR, UK/GBP, IN/INR,
  etc.).
  - ~6–10 **departments** (Engineering, Sales, Marketing, Finance, HR, Ops, Support,
  Product...).
  - **Levels** (e.g. L1–L7 / IC + Manager) with salary bands that scale by level and
  are adjusted by country cost factor → produces realistic, queryable distributions.
  - Manager hierarchy (some employees reference a manager).
  - Hire dates spread over years; mostly active, a few inactive.
- Seed the **fx_rate** table and **one HR user**.
- Seed must be **idempotent** (safe to re-run) and **fast** (batch inserts).
- Provide a small **fixture seed** (e.g. 20 employees with known numbers) for tests so
aggregates can be asserted exactly.

## 5. Proposed folder structure (for later implementation)

```
salary-management/
├─ docs/                 # all artifacts (this folder)
├─ apps/
│  ├─ api/               # FastAPI backend (Python)
│  │  ├─ app/
│  │  │  ├─ main.py      # FastAPI app factory + router registration
│  │  │  ├─ core/        # config, security (JWT), db session
│  │  │  ├─ models/      # SQLAlchemy models
│  │  │  ├─ schemas/     # Pydantic request/response schemas
│  │  │  ├─ routers/     # auth, employees, compensation, analytics, export
│  │  │  ├─ services/    # business logic (validation, fx, history, aggregates)
│  │  │  ├─ repositories/# data access (SQLAlchemy queries)
│  │  │  └─ common/      # money/fx utils, error handlers, deps
│  │  ├─ alembic/        # migrations
│  │  ├─ seeds/          # seed_10k.py + fixture_seed.py
│  │  ├─ tests/          # pytest: unit + integration
│  │  └─ pyproject.toml  # deps (uv/poetry), ruff, black, pytest config
│  └─ web/               # Next.js frontend
│     ├─ app/            # routes: login, employees, employees/[id], dashboard
│     ├─ components/
│     ├─ lib/            # api client, formatting, hooks (TanStack Query)
│     └─ __tests__/
├─ docker-compose.yml
├─ TASK_BACKLOG.md
└─ README.md
```

*(Two top-level apps under `apps/`; could be split into separate repos instead.
Decide at M0.)*

## 6. Testing strategy (TDD-first) — summary

> Full plan in `TASK_BACKLOG.md` Epic G and per-story acceptance criteria.

- **Unit (fast, deterministic):** services with mocked repos — validation bounds,
currency normalization math, history-record creation, median/avg calculations.
- **Integration (API):** pytest + httpx/TestClient against SQLite with fixture seed —
list filters, pagination, edit→history, analytics correctness vs known fixture,
auth guards.
- **UI:** Testing Library — directory renders/filters, edit form validation, dashboard
KPIs render.
- Use the **20-employee fixture** for exact-value assertions; never assert against the
random 10k seed.

## 7. Open design decisions to confirm at M0

- Monorepo vs. two folders.
- Compensation as single current row + history, vs. fully temporal (effective-dated)
rows. *Leaning:* current row + history for v1 simplicity (note upgrade path).
- Analytics: live aggregate query + short TTL cache vs. materialized summary table.
*Leaning:* indexed live query first; add cache/materialization only if measured slow.

