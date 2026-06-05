# Trade-off Explanations

Why I chose what I chose — and what I gave up. The rubric explicitly grades reasoning
about what was deliberately *not* built and which trade-offs were made.

## 1. Scope trade-offs (what we deliberately don't build)

| Decision | Chosen | Alternative | Why this trade-off |
|----------|--------|-------------|--------------------|
| Product surface | **Salary management + analytics** | Full HRIS / payroll engine | The problem is comp data + answering pay questions. Payroll disbursement & tax are huge regulated domains that add risk without serving the core persona. |
| "Answer questions" | **Deterministic dashboards + filters** | LLM natural-language Q&A | On *salary* data, correctness and trust beat novelty. NL Q&A can hallucinate; I keep it as a stretch built on the same query layer. |
| Currency | **Seeded, versioned FX table** | Live FX API | Demonstrates multi-currency normalization without external dependency, rate limits, or non-determinism in tests. |
| Auth | **Single HR user + JWT** | Enterprise SSO + granular RBAC | Persona is one HR Manager. Modeling a `role` leaves the door open; building IAM now is gold-plating. |
| Bulk import | **Stretch goal** | v1 feature | High value (Excel pain) but higher risk (parsing, conflict handling). Export ships in v1; import is queued. |
| Multi-tenancy | **Single org** | SaaS multi-tenant | Brief is one org (ACME). Multi-tenancy would complicate the model with no assessment benefit. |

## 2. Technical trade-offs

### Python FastAPI backend + Next.js/React frontend
- **For:** Python backend per stakeholder direction; FastAPI gives async performance,
  automatic OpenAPI docs, first-class Pydantic validation, and clean dependency
  injection — strong fit for a typed, well-tested API.
- **Against / risk:** two languages (Python + TypeScript) instead of one shared language;
  no compile-time type sharing across the boundary.
- **Verdict:** mitigate the boundary gap by generating a typed FE client from the
  FastAPI OpenAPI schema. Django was the alternative — FastAPI chosen for a lighter,
  API-first footprint (no admin/templating needed here).

### SQLAlchemy 2.0 + Alembic, SQLite (dev/test) / PostgreSQL (prod)
- **For:** mature, expressive ORM with powerful aggregate support, solid migrations,
  near-zero-setup local dev on SQLite, Postgres realism for prod, SQLite determinism
  for tests.
- **Against:** more boilerplate than some ORMs; some advanced aggregates use SQLAlchemy
  Core / raw SQL; SQLite↔Postgres feature gaps (mitigated by keeping queries portable
  and testing on both where it matters).

### Server-side pagination / filtering / aggregation
- **For:** the only sane way to stay fast and memory-safe at 10k+ rows; the DB does what
  it's good at.
- **Against:** larger API surface and more query code than client-side filtering.
- **Verdict:** non-negotiable at this scale.

### Compensation as "current row + immutable history" (vs fully temporal)
- **For:** simple to query "current pay", still gives auditability and change history.
- **Against:** not a complete bitemporal history of every effective-dated state.
- **Verdict:** v1 simplicity; documented upgrade path to effective-dated rows if needed.

### Analytics: live indexed query + optional TTL cache (vs materialized table)
- **For:** simplest correct thing; always fresh; no sync logic.
- **Against:** heavier queries under high concurrency.
- **Verdict:** measure first. Add caching/materialization only if profiling shows need
  (see `docs/PERFORMANCE.md`). Avoid premature optimization.

### Money as integers (vs floats / decimals)
- **For:** no floating-point rounding errors on money — critical for trust.
- **Against:** must format for display and handle conversion carefully.
- **Verdict:** correctness wins; trivial formatting cost.

## 3. Process trade-offs
- **TDD for core logic** (validation, FX math, aggregates, history): pays off because
  these are the parts where bugs are costly and hard to spot. Pure UI glue is tested
  more lightly to keep velocity.
- **Incremental commits per story** (per the brief) over big-bang commits: shows
  evolution, easier to review, aligns with grading on commit history.
- **Docs/artifacts first, then code:** de-risks scope and gets clarifying questions out
  early, matching "clarify requirements before building".

## 4. What would change at larger scale (100k–1M+)
- Materialized/rollup analytics tables refreshed on write or schedule.
- Read replicas; connection pooling; possibly cursor-based pagination.
- Background jobs for heavy exports/imports.
- Caching layer (Redis) for hot aggregates.
These are intentionally **not** built now — see `docs/PERFORMANCE.md` for the rationale
and triggers.
