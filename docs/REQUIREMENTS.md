# Requirements Document — Salary Management (v1)

> One-page requirements as required by the brief. Detail lives in `docs/PRD.md`.

## Goal
Give ACME's **HR Manager** a single, secure, web-based source of truth to **manage**
salary data for **~10,000 employees across multiple countries** and to **answer
questions about how the org pays people** — replacing today's error-prone Excel process.

## In Scope (v1 — what we will build)
**Employee & salary management**
- Browse all employees with fast server-side **search, filter, sort, pagination**.
- View an employee's profile + **current compensation** (base + bonus, currency).
- **Edit** salary/bonus with validation; every change is recorded in an **audit history**.
- Add a new employee; deactivate (soft-delete) an employee.

**Analytics — "how the org pays people"**
- Org dashboard: **headcount, total payroll, average/median pay**, normalized to a
  base currency (USD) via a seeded FX table.
- Breakdowns by **country, department, and job level** (avg/median/min/max, headcount).
- Filters that apply across the dashboard and tables.
- **CSV export** of the current filtered view.

**Foundations**
- Lightweight auth (single seeded HR user, JWT session).
- **Seed script generating 10,000 realistic employees** across countries/departments.
- Automated tests (unit + key integration) that are fast and deterministic.
- Dockerized, one-command local run; deployed demo + short video walkthrough.

## Out of Scope (deliberately left out) + reasoning
| Left out | Why |
|----------|-----|
| Payroll **disbursement**, payslips, tax/withholding | This is a *management & insight* tool, not a payroll engine; tax/compliance is a huge regulated domain that would dwarf the core value. |
| Full **HRIS** (leave, attendance, performance, benefits) | Out of the problem statement; keeps the product focused on compensation. |
| **Live FX** rates / currency trading-grade conversion | A seeded, versioned FX table is enough to demonstrate multi-currency normalization; live feeds add ops complexity with little assessment value. |
| **Enterprise SSO / fine-grained RBAC** | Single HR persona for v1. Auth is modeled so RBAC can be added; building IAM now is gold-plating. |
| **Natural-language Q&A (LLM)** over the data | Core need is answered by deterministic, fast, trustworthy dashboards. NL Q&A is a documented **stretch goal**, not core (sensitive data → correctness > novelty). |
| **CSV bulk import / bulk edit** | High value (maps to their Excel pain) but riskier; included as a **stretch goal**, not v1-critical. |
| **Real-time collaboration / multi-tenant** | Single org, single primary user; no need for live multi-user sync. |
| **Mobile-native apps** | Responsive web is sufficient for an office HR workflow. |

## Key decisions & assumptions (see `questions.md`)
- **Stack (decided):** Python **FastAPI** backend (SQLAlchemy 2.0 + Alembic + Pydantic)
  + **Next.js/React** frontend; PostgreSQL (prod) / SQLite (dev/tests).
- "Salary" = annual base (+ optional bonus), stored with per-employee currency.
- Multi-currency normalized to USD for aggregates using a seeded FX table.
- **"Answer questions" (decided):** deterministic analytics/dashboards in v1; NL Q&A is a
  stretch goal only if time permits.
- Design target: smooth at 10k–50k employees.

## Non-functional requirements
- **Performance:** employee list and analytics respond < ~300 ms at 10k rows (indexed,
  paginated, pre-aggregated where needed).
- **Security:** salary data is access-controlled; no public exposure; changes audited.
- **Quality:** meaningful unit/integration tests; clean, documented, maintainable code.
- **DX:** new dev can clone → seed → run with one or two commands (documented in README).

## Primary success metrics
- Find + open any employee in **< 5 seconds**.
- Update a salary (with history recorded) in **< 10 seconds**, with validation.
- Answer "avg pay by country/department/level" with **no manual spreadsheet work**.
