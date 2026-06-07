# Task Backlog — Salary Management

Epics → Stories → Tasks for the whole build. Stories carry acceptance criteria;
tasks are the concrete work items. We follow **TDD** (write tests first) and make
**small, incremental commits** per the assessment.

**Legend:** `[ ]` todo · `[~]` in progress · `[x]` done · ⭐ stretch (post-v1)

**Suggested build order (milestones):**
`M0 → M1 → M2 → M3 → M4 → M5`, then stretch.

---

## EPIC A — Project Foundations & Tooling  *(Milestone M0)*
> Goal: a runnable, tested skeleton with the 10k seed and CI.

### Story A1 — Repo & tooling setup
**As a developer, I want a clean, typed project skeleton so I can build confidently.**
- [x] A1.1 Decide monorepo vs two folders; init `apps/api` and `apps/web`
- [x] A1.2 TypeScript, ESLint, Prettier, editorconfig
- [x] A1.3 Base scripts: `dev`, `build`, `test`, `lint`, `seed`
- [x] A1.4 `.env.example` + config loading (no secrets committed)
- [x] A1.5 README skeleton (getting started)
**Accept:** `install → dev` runs an empty app; lint+typecheck pass.

### Story A2 — Database & ORM
- [x] A2.1 Add SQLAlchemy 2.0 + Alembic; configure SQLite (dev/test) + Postgres (prod)
- [x] A2.2 Define schema: employee, compensation, salary_change_history, department, fx_rate, user
- [x] A2.3 Add indexes (country, departmentId, level, status, search cols)
- [x] A2.4 Initial migration
**Accept:** migrate runs clean on SQLite and Postgres; schema matches `docs/DESIGN_NOTES.md`.

### Story A3 — Seed script (10,000 employees)
- [x] A3.1 Fixed-seed faker generators (countries+currencies, departments, levels, bands)
- [x] A3.2 Country-adjusted salary bands by level; manager hierarchy; hire dates; statuses
- [x] A3.3 Batched/idempotent inserts; seed fx_rate + one HR user
- [x] A3.4 Tiny deterministic **20-row fixture** seed for tests
- [x] A3.5 Verify counts + spot-check distribution
**Accept:** `seed` creates 10k employees fast & idempotently; fixture seed produces known values.

### Story A4 — CI & containerization
- [x] A4.1 GitHub Actions: install, lint, typecheck, test on PR
- [x] A4.2 Dockerfile(s) for api + web
- [x] A4.3 `docker-compose.yml` (api + web + Postgres)
**Accept:** CI green; `docker-compose up` serves the app locally.

---

## EPIC B — Authentication & Security  *(M4, foundations early)*
### Story B1 — HR login
**As Maya, I must log in so salary data isn't public.**
- [x] B1.1 *(test first)* auth service tests: valid/invalid creds, token issue/verify
- [x] B1.2 `POST /auth/login` → JWT; password hashing (bcrypt/argon2)
- [x] B1.3 JWT guard; protect all `/employees`, `/analytics`, `/export` routes
- [x] B1.4 Web login page + token storage + auth redirect
- [x] B1.5 *(test)* unauthenticated requests rejected (401)
**Accept:** unauthenticated API access returns 401; login works end-to-end.

---

## EPIC C — Employee Directory  *(M1)*
### Story C1 — List employees (paginated)
- [x] C1.1 *(test first)* repo/service: pagination + total count
- [x] C1.2 `GET /employees` with page/pageSize; projected columns + `baseUsd`
- [x] C1.3 Web directory table (shadcn) with page controls + total
- [x] C1.4 Loading skeletons + empty state
**Accept:** lists 10k via pages; default 25; P95 < 300 ms; total shown.

### Story C2 — Search, filter, sort
- [ ] C2.1 *(test first)* query builder: q, country, department, level, status, sort
- [ ] C2.2 Implement combined (AND) server-side filters + sort
- [ ] C2.3 Web filter controls + debounced search; reflect state in URL
- [ ] C2.4 *(test)* filter correctness vs fixture
**Accept:** filters combine; sort by salary/name/hireDate; URL shareable.

---

## EPIC D — Employee Detail, Edit & History  *(M2)*
### Story D1 — View employee detail
- [ ] D1.1 *(test first)* `GET /employees/:id` returns profile + current comp + derived
- [ ] D1.2 Web detail page (profile, base, bonus, currency, monthly, total comp)
**Accept:** all fields shown with currency; 404 handled.

### Story D2 — Edit salary/bonus with validation + history
- [ ] D2.1 *(test first)* validation rules (positive, bounds, currency exists)
- [ ] D2.2 *(test first)* edit writes history row in a transaction (old→new, user, ts)
- [ ] D2.3 `PATCH /employees/:id/compensation`
- [ ] D2.4 Web edit form: validation messages, optimistic/loading state, success toast
**Accept:** invalid blocked w/ clear msgs; success persists; history row created atomically.

### Story D3 — Salary change history view
- [ ] D3.1 *(test)* `GET /employees/:id/history` newest-first, immutable
- [ ] D3.2 Web history panel/timeline
**Accept:** every edit appears; never editable/deletable.

### Story D4 — Create & deactivate employee
- [ ] D4.1 *(test)* create employee + initial compensation; unique email/code
- [ ] D4.2 *(test)* soft-delete sets status=inactive (not hard delete)
- [ ] D4.3 Web add-employee form + deactivate action
**Accept:** new employee appears in list; deactivated excluded by default filter.

---

## EPIC E — Analytics ("how we pay people")  *(M3)*
### Story E1 — Org summary KPIs
- [ ] E1.1 *(test first)* avg & **median** + total payroll math vs fixture (exact values)
- [ ] E1.2 *(test first)* FX normalization to USD via fx_rate
- [ ] E1.3 `GET /analytics/summary` (respects filters)
- [ ] E1.4 Web KPI cards (headcount, total payroll USD, avg, median; fx asOf label)
**Accept:** numbers match fixture exactly; normalized-USD clearly labeled; P95 < 300 ms.

### Story E2 — Breakdowns by dimension
- [ ] E2.1 *(test first)* group-by country/department/level: count, avg, median, min, max
- [ ] E2.2 `GET /analytics/breakdown?groupBy=...`
- [ ] E2.3 Web tables + simple charts (bar) per dimension
- [ ] E2.4 Shared filters apply to dashboard + directory
**Accept:** grouped aggregates correct vs fixture; charts render aggregated data only.

---

## EPIC F — Export  *(M4)*
### Story F1 — CSV export of filtered view
- [ ] F1.1 *(test)* CSV reflects active filters; correct headers/rows
- [ ] F1.2 `GET /export/employees.csv`
- [ ] F1.3 Web "Export CSV" button on directory
**Accept:** downloaded CSV matches on-screen filtered data.

---

## EPIC G — Quality, Tests & Docs  *(continuous)*
### Story G1 — Test strategy execution
- [ ] G1.1 Unit: validation, FX math, median/avg, history creation (mocked repos)
- [ ] G1.2 Integration: list/filter, edit→history, analytics correctness, auth guards
- [ ] G1.3 UI: directory render/filter, edit-form validation, dashboard KPIs
- [ ] G1.4 Ensure suite is fast (<~30s) & deterministic; coverage on core
**Accept:** all green in CI; aggregates asserted on fixture; no flaky/network tests.

### Story G2 — Performance verification
- [ ] G2.1 Benchmark `/employees` & `/analytics/summary` on 10k; record in README
- [ ] G2.2 Add/adjust indexes if P95 > budget
**Accept:** documented numbers meet the < 300 ms budget (or trigger noted in PERFORMANCE.md).

### Story G3 — Documentation & DX
- [ ] G3.1 README: setup, seed, run, test, deploy, demo, env vars
- [ ] G3.2 Architecture diagrams linked; API summary; "new dev in 5 min" path
- [ ] G3.3 Keep `docs/AI_USAGE.md` prompt log updated as we build
**Accept:** a new dev can clone → seed → run from README alone.

---

## EPIC H — Deployment & Demo  *(M5)*
### Story H1 — Deploy
- [ ] H1.1 Deploy frontend (Vercel) + API/DB (Render/Fly) — confirm platform (Q13)
- [ ] H1.2 Production env config + seeded demo data
- [ ] H1.3 Smoke test deployed app
**Accept:** public demo URL works (auth-gated); seeded data present.

### Story H2 — Demo video & walkthrough
- [ ] H2.1 Write demo script (search → edit → history → dashboard → export)
- [ ] H2.2 Record short walkthrough video; link in README
**Accept:** video shows the core flows working.

---

## EPIC I — Stretch Goals ⭐ *(only after v1 complete)*
### Story I1 — CSV bulk import / bulk edit ⭐
- [ ] I1.1 Upload + parse + validate + preview diffs
- [ ] I1.2 Apply with per-row error handling + history
### Story I2 — Natural-language Q&A ⭐
- [ ] I2.1 Map NL questions → safe parameterized analytics queries (no free SQL)
- [ ] I2.2 Guardrails: scope to allowed dimensions; show the computed query for trust
### Story I3 — Read-only Finance role + RBAC ⭐
- [ ] I3.1 Role on user; guard write routes; read-only UI mode

---

## Dependency / sequencing notes
- A (foundations) blocks everything.
- B (auth) can be stubbed early, hardened at M4.
- C → D → E build on the employee/comp model from A2.
- G runs **throughout** (TDD per story), not at the end.
- H is last; needs a working v1.

## Definition of Done (every story)
- Tests written first, meaningful, deterministic, and passing.
- Lint + typecheck clean.
- Hot paths within performance budget (or trigger documented).
- Auth enforced on data routes; no salary leakage.
- Docs updated; small, descriptive commit(s).
