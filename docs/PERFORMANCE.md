# Performance Considerations

The rubric grades performance from a **UX point of view** — "does it feel smooth and
fast where it matters?" — at the seed scale of **10,000 employees**.

## 1. Where performance matters (and where it doesn't)
| Hot path (must feel instant) | Cold path (fine if slower) |
|------------------------------|-----------------------------|
| Employee directory: search/filter/sort/paginate | Seed script runtime |
| Opening an employee detail | CSV export of full dataset |
| Dashboard KPIs + breakdowns | One-off migrations |
| Saving a salary edit | |

Budget for hot paths: **P95 < ~300 ms** server response at 10k rows; UI interaction
feels immediate (skeletons/optimistic updates mask any latency).

## 2. Strategies

### Database
- **Indexes** on every filter/sort column: `country`, `departmentId`, `level`,
  `status`, `hireDate`, plus search columns (`lastName`, `email`, `employeeCode`).
- **Composite indexes** for common filter+sort combos if profiling shows need.
- **Server-side pagination** (LIMIT/OFFSET for v1; cursor-based if deep paging matters).
- **Aggregates run in the DB** (GROUP BY) — never load 10k rows into app memory to sum.
- **Integer money** keeps arithmetic cheap and exact.

### API
- Return only the columns the list needs (no over-fetching).
- Compute derived values (`monthlyBase`, `baseUsd`) in the query/projection.
- **Short-TTL in-memory cache** for analytics responses keyed by filter set — only if
  measured necessary (avoid premature optimization).
- Consistent, small JSON payloads; gzip/compression at the edge.

### Frontend
- **TanStack Query**: caching, `keepPreviousData` for smooth pagination, background
  refetch.
- **Debounced search** input to avoid request floods.
- **Skeleton/loading states** and **optimistic updates** on edit so the UI feels instant.
- Charts kept lightweight; render aggregated data (handful of points), not 10k rows.
- Avoid shipping the whole dataset to the client — ever.

## 3. Seeding 10k efficiently
- **Batch inserts** (SQLAlchemy `bulk_insert_mappings` / chunked inserts) rather than
  10k individual `INSERT`s.
- Fixed random seed → reproducible and fast.
- Idempotent (truncate/upsert) so re-running is safe.

## 4. How we'll verify (not just claim)
- A small **benchmark note**: time the `/employees` list and `/analytics/summary`
  endpoints against the seeded 10k DB and record numbers in the README.
- Assert **correctness** of aggregates against the deterministic 20-row fixture in tests.
- Keep the **test suite fast** (< ~30 s): SQLite in-memory for unit tests, minimal
  fixtures, no network.

## 5. Scaling triggers (when to add complexity)
We deliberately start simple. Add the next lever **only when measurements cross the
threshold**:

| Symptom (measured) | Lever to add |
|--------------------|--------------|
| List P95 > 300 ms at target scale | composite indexes; cursor pagination |
| Analytics P95 > 300 ms or high concurrency | TTL cache → materialized rollup table |
| Export blocks requests | move export to a background job + download link |
| DB CPU bound on reads | read replica + connection pooling |
| Hot aggregates dominate | Redis cache |

Documenting these triggers (rather than building them now) is itself the trade-off:
keep v1 lean and correct, with a clear, evidence-based path to scale.
