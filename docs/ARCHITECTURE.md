# Architecture

> Diagrams use Mermaid so they render in GitHub. Decisions are captured as ADRs at the
> bottom. Stack assumptions are in `questions.md` / `docs/REQUIREMENTS.md`.

## 1. System context (C4 — Level 1)

```mermaid
flowchart LR
    HR["HR Manager (Maya)\nbrowser"] -->|HTTPS| FE["Next.js Web App\n(React UI)"]
    FE -->|REST/JSON + JWT| API["FastAPI (Python)\nbackend"]
    API -->|SQLAlchemy ORM| DB[("PostgreSQL\n(SQLite in dev/test)")]
    API --> FX["FX Rate table\n(seeded, versioned)"]
    Seed["Seed script\n(10k employees)"] --> DB
```

## 2. Container / component view (C4 — Level 2)

```mermaid
flowchart TB
    subgraph Frontend["Next.js (App Router)"]
        Pages["Pages: Login, Directory, Employee Detail, Dashboard"]
        UIComp["UI components (shadcn/ui + Tailwind)"]
        DataLayer["Data layer: TanStack Query + API client"]
    end

    subgraph Backend["FastAPI (Python)"]
        AuthR["Auth router (JWT dependency)"]
        EmpR["Employees router\nrouter / service / repository"]
        CompR["Compensation + History service"]
        AnalyticsR["Analytics service\n(aggregate queries + cache)"]
        ExportR["Export router (CSV)"]
        Common["Common: Pydantic schemas, exception handlers, logging"]
    end

    DataLayer -->|HTTP| AuthR
    DataLayer --> EmpR
    DataLayer --> CompR
    DataLayer --> AnalyticsR
    DataLayer --> ExportR
    EmpR --> ORM["SQLAlchemy session"]
    CompR --> ORM
    AnalyticsR --> ORM
    ExportR --> ORM
    ORM --> DB[("Relational DB")]
```

## 3. Layered backend design

```mermaid
flowchart LR
    C["Router\n(HTTP, Pydantic validation)"] --> S["Service\n(business logic)"]
    S --> R["Repository\n(SQLAlchemy queries)"]
    R --> DB[("DB")]
    S -.-> Cache["Analytics cache\n(in-memory / TTL)"]
```

- **Router**: request/response, input validation via Pydantic schemas, auth dependency.
- **Service**: business rules (validation bounds, currency normalization, history writes).
- **Repository**: data access, transactions, optimized aggregate SQL.
- Clear separation keeps logic testable (services unit-tested with mocked repos).

## 4. Key flows

### 4.1 Edit salary (with history + transaction)
```mermaid
sequenceDiagram
    participant UI
    participant API as Compensation Service
    participant DB
    UI->>API: PATCH /employees/:id/compensation {baseAnnual, bonus}
    API->>API: validate (positive, bounds, currency)
    API->>DB: BEGIN TX
    API->>DB: read current compensation
    API->>DB: update compensation
    API->>DB: insert SalaryChangeHistory (old→new, user, ts)
    API->>DB: COMMIT
    API-->>UI: 200 updated compensation
```

### 4.2 Analytics query (normalized + cached)
```mermaid
sequenceDiagram
    participant UI
    participant A as Analytics Service
    participant Cache
    participant DB
    UI->>A: GET /analytics/summary?country=DE&department=Eng
    A->>Cache: lookup(key=filters)
    alt hit
        Cache-->>A: aggregates
    else miss
        A->>DB: grouped aggregate query (JOIN fx_rate → USD)
        DB-->>A: rows
        A->>Cache: store(TTL)
    end
    A-->>UI: KPIs + breakdowns
```

## 5. Data model (ER)

```mermaid
erDiagram
    USER ||--o{ SALARY_CHANGE_HISTORY : "changes"
    DEPARTMENT ||--o{ EMPLOYEE : has
    EMPLOYEE ||--o{ EMPLOYEE : "manages (managerId)"
    EMPLOYEE ||--|| COMPENSATION : "current"
    EMPLOYEE ||--o{ SALARY_CHANGE_HISTORY : "audited by"
    CURRENCY ||--o{ EMPLOYEE : "paid in"
    CURRENCY ||--o{ FX_RATE : "rate to USD"

    EMPLOYEE {
        uuid id PK
        string employeeCode
        string firstName
        string lastName
        string email
        uuid departmentId FK
        string jobTitle
        string level
        string country
        string currency FK
        uuid managerId FK
        date hireDate
        string employmentType
        string status
    }
    COMPENSATION {
        uuid id PK
        uuid employeeId FK
        bigint baseAnnual
        bigint bonusAnnual
        string currency
        date effectiveDate
        bool isCurrent
    }
    SALARY_CHANGE_HISTORY {
        uuid id PK
        uuid employeeId FK
        string field
        bigint oldValue
        bigint newValue
        uuid changedBy FK
        datetime changedAt
        string note
    }
    DEPARTMENT { uuid id PK
        string name }
    FX_RATE { string currency PK
        decimal rateToUsd
        date asOf }
    USER { uuid id PK
        string email
        string passwordHash
        string role }
```

## 6. Tech stack (decided — see questions.md)
| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | **Next.js (App Router) + React + TypeScript** | Modern, fast, SSR-capable, great DX. |
| UI kit | **shadcn/ui + Tailwind** | Clean, accessible, fast to build a polished UI. |
| Data fetching | **TanStack Query (React Query)** | Caching, loading/error states, pagination ergonomics. |
| Backend | **FastAPI (Python 3.12)** | Fast, async, auto OpenAPI docs, Pydantic validation, clean DI. |
| Validation | **Pydantic v2** | Typed request/response schemas at the boundary. |
| ORM | **SQLAlchemy 2.0 + Alembic** | Mature, powerful queries + migrations; SQLite↔Postgres parity. |
| DB | **PostgreSQL** (prod) / **SQLite** (dev/test) | Brief allows SQLite; Postgres for prod realism. |
| Auth | **JWT** (python-jose) + **passlib/bcrypt** (single HR user seeded) | Lightweight, sufficient for v1. |
| Tests | **pytest** (+ httpx/TestClient API, Testing Library UI) | Fast, deterministic, standard. |
| Lint/format | **ruff + black** (BE), **ESLint + Prettier** (FE) | Industry-standard quality gates. |
| Packaging | **Docker + docker-compose** | One-command run; parity. |
| CI | **GitHub Actions** | Lint, typecheck, test on PR. |

## 7. Environments & deployment
- **Local:** `docker-compose up` → API + Postgres + web; or SQLite for zero-infra dev.
- **Test:** SQLite (in-memory/file) with fixed-seed fixtures for determinism.
- **Prod/demo:** Frontend → Vercel; API + Postgres → Render/Fly (documented). Confirm
  platform (questions.md Q13).

## 8. Cross-cutting concerns
- **Validation:** Pydantic schemas at the boundary; service-level invariants.
- **Errors:** consistent JSON error shape; global exception handlers.
- **Money:** stored as integer minor units (or integer base units) to avoid float error;
  currency always paired with amount.
- **Currency normalization:** join to `fx_rate` (versioned `asOf`) for USD aggregates.
- **Security:** auth guard on all data routes; no salary data on public endpoints;
  audit history on changes; secrets via env.
- **Observability:** structured request logging; basic health endpoint.

## 9. Architecture Decision Records (ADRs)
> Lightweight ADR format: Context → Decision → Consequences. Detail/alternatives in
> `docs/TRADEOFFS.md`.

- **ADR-001 — Python FastAPI backend + Next.js/React frontend.** Python backend per
  stakeholder direction; FastAPI gives async performance, auto OpenAPI docs, and
  Pydantic validation. *Consequence:* two languages (Python + TS); typed contract shared
  via OpenAPI rather than a single language.
- **ADR-002 — SQLAlchemy 2.0 + Alembic, relational DB with SQLite/Postgres parity.**
  Mature ORM + migrations, easy local dev on SQLite. *Consequence:* some advanced
  aggregates via SQLAlchemy Core / raw SQL.
- **ADR-003 — Server-side pagination/filtering/aggregation.** Required for 10k rows to
  stay fast. *Consequence:* more API surface vs. client-side filtering.
- **ADR-004 — Store amounts as integers + per-employee currency; normalize via FX
  table.** Avoids float errors, supports multi-country. *Consequence:* seeded (not live)
  FX rates.
- **ADR-005 — Immutable salary-change history.** HR trust/auditability. *Consequence:*
  extra writes per edit (acceptable).
- **ADR-006 — Deterministic analytics over LLM Q&A for core.** Correctness on sensitive
  data > novelty; NL Q&A is a stretch. *Consequence:* "questions" answered via
  dashboards/filters.
