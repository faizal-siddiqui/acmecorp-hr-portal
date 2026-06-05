# High-Level Problem Statement

## In one sentence
Replace ACME's error-prone, Excel-based salary management with a fast, secure,
web-based application that lets an HR Manager **maintain** salary data for ~10,000
employees across multiple countries and **answer questions** about how the
organization pays its people.

## The pain today
- Salary data for **10,000 employees** lives in **spreadsheets across multiple
  countries**.
- Excel is **tedious, error-prone, and hard to query** — no single source of truth,
  no reliable aggregation, risky to share sensitive pay data, and easy to break with a
  bad formula or paste.
- The HR Manager cannot easily answer questions like *"What do we pay engineers in
  Germany on average?"* or *"What is our total monthly payroll by department?"*

## Who we're building for
**Primary persona — HR Manager ("Maya")**
- Owns the integrity of org-wide compensation data.
- Needs to find, view, and update an employee's salary quickly and confidently.
- Is regularly asked leadership/finance questions about pay and must answer accurately.
- Is **not** a data analyst or engineer — the tool must be intuitive and require little
  thought about "how it works".

## What success looks like
1. **Single source of truth** for salary data — replaces the spreadsheets.
2. **Fast & confident editing** — find any of 10k employees and update pay in seconds,
   with validation and an audit/history of changes.
3. **Answers, not raw rows** — dashboards and reports that summarize pay by country,
   department, level, and currency, with org-wide totals normalized to a base currency.
4. **Trustworthy** — sensitive data is access-controlled and changes are traceable.
5. **Feels instant** at 10k records — pagination, search, and analytics stay smooth.

## The core jobs-to-be-done
| # | As the HR Manager, I want to… | So that… |
|---|-------------------------------|----------|
| 1 | search/filter and browse all employees | I can find anyone fast |
| 2 | view an employee's compensation details | I have the full picture |
| 3 | update salary/bonus with validation | data stays correct |
| 4 | see the history of changes to a salary | I can trust and explain it |
| 5 | see org-wide pay analytics by dimension | I can answer leadership's questions |
| 6 | export data / reports | I can share with finance |

## Explicitly framing what this is *not*
- Not a full HRIS, payroll-disbursement, or benefits-administration system.
- Not a tax/compliance engine.
- Not a multi-tenant SaaS — it's one organization (ACME).

See `docs/REQUIREMENTS.md` for the one-page scope and `docs/PRD.md` for detail.
