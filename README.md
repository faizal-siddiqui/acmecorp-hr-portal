# Salary Management System

HR salary management system for ACME Corp — employee directory, compensation analytics, and history tracking.

## 🚀 Quick Start (5-minute path)

### Option A: Automatic Setup (Recommended)

Run the setup script for your platform. This will install all dependencies, set up environment files, seed the database, and start the development servers.

**macOS / Linux:**
```bash
./run-dev.sh
```

**Windows (PowerShell):**
```powershell
./run-dev.ps1
```

---

### Option B: Manual Setup

```bash
# 1. Clone and install all dependencies
npm install && cd apps/web && npm install && cd ../..
cd apps/api && uv sync && cd ../..

# 2. Setup environment
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local

# 3. Seed the database (10,000 records)
npm run seed

# 4. Run the app
npm run dev
```

- **Web**: [http://localhost:3000](http://localhost:3000) (Login: `admin@acme.com` / `admin123`)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Project Structure

This is a monorepo containing:

- **`apps/api`**: FastAPI backend (Python 3.12+)
- **`apps/web`**: Next.js frontend (TypeScript)
- **`docs`**: Design notes and architectural documentation

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy 2.0 (Async), Pydantic v2, `uv` for package management.
- **Frontend**: Next.js (App Router), Tailwind CSS, Shadcn UI, TanStack Query.
- **Database**: SQLite (Development/Testing), PostgreSQL (Production).

## Environment Variables

### Backend (`apps/api/.env`)
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite+aiosqlite:///./salary.db` |
| `SECRET_KEY` | JWT signing key | `change-me-in-production` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000` |

### Frontend (`apps/web/.env.local`)
| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |

## API Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | `POST` | Authenticate and get JWT |
| `/employees/` | `GET` | Paginated list with filters/search |
| `/employees/{id}` | `GET` | Detailed employee view |
| `/employees/{id}/compensation` | `PATCH` | Update salary (creates history) |
| `/analytics/summary` | `GET` | Global KPIs (Avg, Median, etc.) |
| `/analytics/breakdown` | `GET` | Grouped stats by country/dept/level |
| `/export/employees.csv` | `GET` | Export filtered list to CSV |

## Performance

The system is designed to handle 10,000+ employee records with sub-300ms response times for all critical paths.

### Benchmark Results (10k employees)

| Endpoint | Avg Latency | P95 Latency |
|----------|-------------|-------------|
| `/employees/` (List) | ~26 ms | ~28 ms |
| `/analytics/summary` | ~55 ms | ~106 ms |
| `/employees/?q=John` | ~47 ms | ~55 ms |

For detailed performance strategy, see [docs/PERFORMANCE.md](docs/PERFORMANCE.md).

## Development Workflow

### Testing
We follow a TDD-first approach. Run all tests:
```bash
npm test
```

### Linting & Formatting
```bash
npm run lint    # Check for linting errors
npm run format  # Auto-format code
```

## Deployment

### Frontend (Vercel)
The frontend is a standard Next.js app. Point Vercel to the `apps/web` directory and set `NEXT_PUBLIC_API_URL`.

### Backend (Docker/Render/Fly)
The backend can be containerized using the provided `Dockerfile` (to be added) or deployed directly to a Python-capable host. Ensure `DATABASE_URL` points to a persistent PostgreSQL instance in production.

## Documentation

- [Architecture & Diagrams](docs/ARCHITECTURE.md)
- [Product Requirements (PRD)](docs/PRD.md)
- [Design Notes & API Contract](docs/DESIGN_NOTES.md)
- [AI Usage & Prompt Log](docs/AI_USAGE.md)
- [Task Backlog](TASK_BACKLOG.md)
