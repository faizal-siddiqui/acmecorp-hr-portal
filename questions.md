# Clarifying Questions

> Per the assessment ("Ask Questions — Don't Assume"), here are the open questions that
> affect scope and design. Where an answer is needed to keep moving, I have stated a
> **working assumption** that I will proceed with unless told otherwise. These assumptions
> are also recorded in `docs/REQUIREMENTS.md` and `docs/PRD.md`.

## 1. Tech Stack / Job Description

1. The brief says "Language & Framework as per JD". I don't have the JD. Which backend
   stack should I target?
   - **DECIDED (per your feedback):** **Python backend** with a **React/Next.js**
     frontend. Backend = **FastAPI + Pydantic v2 + SQLAlchemy 2.0 + Alembic**, with
     **PostgreSQL** in production and **SQLite** for local/dev + tests. (Django was the
     alternative; FastAPI chosen for a clean, fast, well-typed API.)
2. Is there a preferred component library (MUI, Ant Design, shadcn/ui, Chakra)?
   - **Working assumption:** shadcn/ui + Tailwind for a clean, modern, accessible UI.

## 2. Users, Auth & Permissions

3. Persona is "HR Manager". Is this single-role, or do we also need Admin / read-only
   Viewer / Finance roles?
   - **Working assumption:** Single role (HR Manager) for v1, with auth modeled so RBAC
     can be added later. (Auth itself may be stubbed/simple — see Q4.)
4. Is real authentication (login, password hashing, sessions/JWT) in scope, or is a
   single trusted HR user acceptable for this assessment?
   - **Working assumption:** Lightweight auth (single seeded HR user, JWT session) so the
     app isn't wide open, but SSO/enterprise IAM is explicitly out of scope.
5. Is an audit trail of *who changed what salary and when* required?
   - **Working assumption:** Yes, a basic immutable salary-change history is in scope
     (HR cares about this), but full audit logging of every action is out of scope.

## 3. Data Model & Salary Semantics

6. "Salaries across multiple countries" — do we need **multi-currency** support
   (store currency per employee, convert for org-wide reporting)?
   - **Working assumption:** Yes. Store amount + currency per employee. For aggregate
     reporting, normalize to a single base currency (e.g. USD) using a **static/seeded
     FX rate table** (live FX feeds are out of scope).
7. What does "salary" mean precisely — base salary only, or base + bonus + equity +
   allowances (total compensation)?
   - **Working assumption:** Base salary (annual) + optional bonus, stored as structured
     fields. Equity/benefits are out of scope for v1.
8. Pay frequency — do we model annual, monthly, hourly? Different countries differ.
   - **Working assumption:** Store an **annual base** as the canonical figure; display
     monthly as a derived value. Hourly/contractor pay is out of scope.
9. What employee attributes matter for "how the org pays people" analysis?
   - **Working assumption:** department, job title/level, country/location, employment
     type (full-time), hire date, manager, currency, base salary, bonus, status.

## 4. "Answer questions about how the org pays people"

10. How literal is "answer questions"? Options:
    - (a) Rich dashboards + filters + structured reports (deterministic), **or**
    - (b) A natural-language Q&A box ("What's the average salary in Germany for
      engineers?") backed by an LLM / query engine.
    - **DECIDED (per your feedback):** Deliver (a) — fast, deterministic analytics
      (averages, medians, distributions, pay-gap by dimension, headcount, payroll cost)
      with strong filtering — for v1. (b) natural-language Q&A is a **stretch goal**,
      built only if time permits, on top of the same query layer.

## 5. Scale & Performance

11. 10,000 employees is the seed size. Is that the steady-state ceiling, or should the
    design target growth (100k+)?
    - **Working assumption:** Design for ~10k–50k cleanly (indexed queries, server-side
      pagination, pre-aggregated analytics). Note the path to larger scale, but don't
      over-engineer for millions.
12. Any expectation around bulk operations (CSV import/export of salaries) given they
    come from Excel today?
    - **Working assumption:** CSV **export** in scope; CSV **import/bulk-edit** is a
      strong stretch goal (it maps directly to their Excel pain) — included in the
      backlog but flagged as optional for v1.

## 6. Deployment & Demo

13. Where should the "deployed software" live (Vercel + Render/Fly/Railway, a single
    container, etc.)? Any cloud constraints?
    - **Working assumption:** Dockerized app + docker-compose for one-command local run;
      deploy frontend to Vercel and backend+DB to Render/Fly (documented). Confirm if a
      specific platform is required.
14. The brief mentions a video demo — is a screen-recorded walkthrough sufficient?
    - **Working assumption:** Yes, a short recorded walkthrough + a demo script in docs.

## 7. Compliance / Sensitivity

15. Salary data is highly sensitive. Are there compliance constraints (PII handling,
    data residency, encryption-at-rest) I should explicitly address?
    - **Working assumption:** Treat as sensitive: access-controlled, no public exposure,
      note encryption/residency as production concerns, but don't implement full
      compliance tooling for this assessment.

---

### Decision log
- **2026-06-04 — Stack:** Python backend (FastAPI + SQLAlchemy + Alembic + Pydantic) +
  React/Next.js frontend. *(Confirmed by user.)*
- **2026-06-04 — "Answer questions":** Deterministic dashboards in v1; NL Q&A is a
  stretch goal only if time permits. *(Confirmed by user.)*

For all remaining open questions, I will proceed with the **working assumptions above**
so the project keeps moving, and I'll clearly mark every assumption in the requirements
and PRD.
