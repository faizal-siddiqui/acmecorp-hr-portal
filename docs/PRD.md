# Product Requirements Document (PRD) — Salary Management


|             |                                                           |
| ----------- | --------------------------------------------------------- |
| **Product** | ACME Salary Management                                    |
| **Version** | v1 (assessment scope)                                     |
| **Author**  | (candidate)                                               |
| **Status**  | Draft — assumptions pending confirmation (`questions.md`) |
| **Persona** | HR Manager ("Maya")                                       |


---

## 1. Overview

A web application that is the single source of truth for ACME's employee compensation
data (~10,000 employees, multiple countries) and lets the HR Manager answer questions
about how the organization pays people. Replaces spreadsheets.

## 2. Goals & Non-Goals

**Goals**

- G1. Maintain accurate salary data for ~10k employees with confidence.
- G2. Find and edit any employee's pay in seconds, with validation + change history.
- G3. Answer org-level pay questions via fast, trustworthy analytics.
- G4. Be intuitive for a non-technical HR Manager.
- G5. Demonstrate production-quality engineering (tests, structure, performance).

**Non-Goals** (see `docs/REQUIREMENTS.md` for reasoning)

- Enterprise SSO / granular RBAC, multi-tenant, mobile-native.
- Live FX feeds; LLM natural-language Q&A (stretch only).

## 3. Personas

- **Maya — HR Manager (primary):** owns comp data; answers leadership/finance questions;
non-technical; values speed, clarity, correctness.
- *(Future) Finance / Leadership viewer (read-only)* — out of scope v1, design allows.

## 4. User Stories (acceptance-oriented)

> Full breakdown with tasks in `TASK_BACKLOG.md`. Summary here.

### Epic A — Employee Directory

- **US-A1**: As Maya, I can see a paginated list of all employees with key columns
(name, title, department, country, base salary, status).
  - *Accept:* loads < 300 ms at 10k rows; default page size 25; total count shown.
- **US-A2**: I can search by name/email/employee-id and filter by country, department,
level, and status; sort by salary/name/hire date.
  - *Accept:* filters combine (AND); server-side; URL reflects state; empty-state shown.

### Epic B — Employee & Compensation Detail

- **US-B1**: I can open an employee and see profile + current compensation
(base, bonus, currency, monthly-derived, total comp).
- **US-B2**: I can edit base salary and bonus with validation (positive, within sane
bounds, currency required).
  - *Accept:* invalid input blocked with clear messages; success confirmed; optimistic
  UI or clear loading state.
- **US-B3**: I can view the **change history** for a salary (old → new, who, when, note).
  - *Accept:* every edit creates an immutable history record; newest first.
- **US-B4**: I can add a new employee and deactivate (soft-delete) one.

### Epic C — Analytics ("how we pay people")

- **US-C1**: I see an org dashboard: headcount, total annual payroll, average & median
base pay — all normalized to a base currency (USD).
- **US-C2**: I see breakdowns by **country, department, and level**
(headcount, avg, median, min, max) as tables + simple charts.
- **US-C3**: Dashboard respects the same filters as the directory.
  - *Accept:* aggregates are correct vs. a known seeded fixture; respond < 300 ms.

### Epic D — Export

- **US-D1**: I can export the current filtered employee list to CSV.

### Epic E — Auth & Security

- **US-E1**: I must log in as the HR user; unauthenticated access is rejected.
- **US-E2**: Salary endpoints require auth; no public data exposure.

### Epic F — Platform / Foundations (engineering)

- Seed 10k employees; Dockerized run; tests; CI; docs.

### Stretch (documented, not v1-critical)

- **US-S1**: CSV bulk import / bulk salary update.
- **US-S2**: Natural-language Q&A over compensation data.
- **US-S3**: Read-only Finance role + RBAC.

## 5. Functional Requirements

1. **Directory**: server-side pagination, search, multi-filter, sort.
2. **Detail**: view/edit base + bonus + currency; derived monthly & total comp.
3. **History**: immutable salary-change log per employee.
4. **Analytics**: org KPIs + grouped aggregates with currency normalization.
5. **Export**: CSV of filtered view.
6. **Auth**: login, protected API, session via JWT.
7. **Seed**: deterministic, realistic 10k dataset (Python Faker + fixed seed).

## 6. Data Model (summary — detail in `docs/DESIGN_NOTES.md`)

- **Employee**: id, employeeCode, firstName, lastName, email, departmentId, jobTitle,
level, country, currency, managerId, hireDate, employmentType, status.
- **SalaryRecord / Compensation**: employeeId, baseAnnual, bonusAnnual, currency,
effectiveDate, (current flag).
- **SalaryChangeHistory**: employeeId, field, oldValue, newValue, changedBy, changedAt,
note.
- **Department**, **Country/Location**, **FxRate** (currency → USD, versioned).
- **User** (HR Manager): id, email, passwordHash, role.

## 7. UX Principles

- Minimal clicks for the top tasks (search → open → edit).
- Sensible defaults, clear validation, obvious empty/loading/error states.
- Money always shown with currency; aggregates clearly labeled "normalized to USD".
- Responsive, accessible (keyboard, contrast, labels).

## 8. Non-Functional Requirements

- **Performance:** P95 < 300 ms for list & analytics at 10k rows; indexed queries;
pagination; pre-aggregation/caching where needed.
- **Security:** auth on all data routes; salary data never public; audit history.
- **Reliability:** deterministic seed; migrations; safe edits (transactions).
- **Maintainability:** layered architecture, typed end-to-end, tested, documented.
- **Portability:** Docker + docker-compose; SQLite (dev/test) / Postgres (prod) parity.

## 9. Success Metrics

- Find+open any employee < 5 s; edit+record history < 10 s.
- Analytics answer top 3 leadership questions with zero manual spreadsheet work.
- Test suite runs fast (< ~30 s) and is deterministic in CI.

## 10. Risks & Mitigations


| Risk                       | Mitigation                                                          |
| -------------------------- | ------------------------------------------------------------------- |
| Slow at 10k rows           | Server-side pagination, indexes, aggregate queries, caching.        |
| Multi-currency confusion   | Always show currency; label normalized USD aggregates.              |
| Sensitive data exposure    | Auth on all routes, no public endpoints, audit history.             |
| Scope creep (HRIS/payroll) | Strict non-goals; stretch items clearly separated.                  |
| Flaky/slow tests           | Fixed-seed fixtures, SQLite in-memory for unit, deterministic data. |


## 11. Release / Milestones

1. **M0 Foundations** — repo, stack, schema, seed (10k), CI.
2. **M1 Directory** — list/search/filter/sort/paginate.
3. **M2 Detail + Edit + History.**
4. **M3 Analytics dashboard.**
5. **M4 Auth + Export + polish.**
6. **M5 Deploy + demo video + docs.**
7. **Stretch** — import, NL Q&A, RBAC.

