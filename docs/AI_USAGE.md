# AI Usage — Strategy, Prompts & Guardrails

The brief explicitly asks us to use AI intentionally and to commit "prompts or
instructions used with AI tools". This documents *how* AI is used, *where* it's trusted,
and *how correctness/quality are maintained*.

## 1. Principles
- **AI accelerates, the engineer decides.** Every AI output is reviewed; nothing on a
  hot/correctness path (FX math, aggregates, validation, money handling) ships without
  a test.
- **Delegate breadth, own depth.** Use AI for scaffolding, boilerplate, test stubs,
  docs, and exploration; keep human judgment on architecture, data model, trade-offs,
  and security.
- **Tests are the contract.** TDD: write/curate tests first, let AI help implement to
  green, then review.
- **Clarify, don't assume.** AI is used to *surface* questions and assumptions (see
  `questions.md`), not to paper over them.

## 2. Where AI is used (and how much it's trusted)
| Area | AI role | Trust level / control |
|------|---------|-----------------------|
| Requirements & artifacts (these docs) | Draft + structure | High value; human edits for correctness of scope/assumptions |
| Architecture & ADRs | Propose options, diagrams | Human picks & justifies trade-offs |
| Boilerplate/scaffold (routers, schemas, config) | Generate | Reviewed, low risk |
| Core business logic (FX, aggregates, validation) | Assist | **Test-gated**; never trusted blindly |
| Tests | Generate cases, edge cases | Human curates assertions; verify they can fail |
| Seed script | Generate realistic distributions | Verified via fixture + spot checks |
| Debugging | Hypotheses, fixes | Verified by reproducing + re-running tests |

## 3. Workflow with AI (per story)
1. Restate the story + acceptance criteria as the prompt context.
2. Ask AI to draft the **test cases** from acceptance criteria (TDD).
3. Review/curate tests; ensure they fail first.
4. Ask AI to implement to green within the established structure.
5. Run lint/typecheck/tests; review diff for correctness, security, style.
6. Commit a small, focused increment with a descriptive message.

## 4. Reusable prompt templates
> Kept generic; concrete prompts will be appended to the "Prompt log" as work proceeds.

**Spec → tests**
```
Given this user story and acceptance criteria: <paste>.
Stack: FastAPI + SQLAlchemy 2.0 (SQLite test) + pytest/httpx.
Write deterministic unit/integration tests first (no network, fixed-seed fixture).
List edge cases you're covering. Don't implement yet.
```

**Tests → implementation**
```
Implement <router/service> to satisfy these tests: <paste/refer>.
Follow the layered structure (router → service → repository).
Validate inputs with Pydantic schemas. Keep money as integers. Don't change the tests.
```

**Review / hardening**
```
Review this diff for correctness, security (authz on data routes, no salary leakage),
error handling, and performance at 10k rows. Flag risky assumptions.
```

**Seed**
```
Write an idempotent Python (SQLAlchemy) seed for 10,000 employees: 8-12 countries w/
currencies, 6-10 departments, levels L1-L7 with country-adjusted salary bands, manager
hierarchy, fixed Faker seed, batched inserts. Also seed fx_rate and one HR user.
```

## 5. Guardrails for correctness & quality
- **Determinism:** fixed seeds; SQLite in-memory; no live FX or network in tests.
- **Exact-value checks:** aggregates asserted against a known 20-row fixture, never the
  random 10k seed.
- **Security review pass** on every endpoint: auth guard present, no public salary data.
- **No hallucinated APIs:** lint (ruff) + optional mypy + tests catch invented methods;
  SQLAlchemy models + Pydantic schemas guard the data layer.
- **Human sign-off** on architecture, data model, and any trade-off before it's locked.

## 6. Prompt log
A running log of notable prompts and outcomes will be appended here as implementation
proceeds (kept concise: prompt intent → what was accepted/changed → why). This makes the
AI collaboration auditable, per the rubric's "AI usage effectiveness".

| Date | Intent | Outcome / human change |
|------|--------|------------------------|
| (M0) | Generate requirements + artifacts + backlog | Accepted with edits to scope assumptions and non-goals |
| 2026-06-07 | Update documentation & DX (Story G3) | Updated root README with 5-min path, API summary, env vars, and deployment notes. |
