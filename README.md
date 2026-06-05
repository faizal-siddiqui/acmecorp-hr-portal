# Salary Management System

HR salary management system for ACME Corp — employee directory, compensation analytics, and history tracking.

## Project Structure

This is a monorepo containing:

- **`apps/api`**: FastAPI backend (Python 3.12+)
- **`apps/web`**: Next.js frontend (TypeScript)
- **`docs`**: Design notes and architectural documentation

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy 2.0 (Async), Pydantic v2, `uv` for package management.
- **Frontend**: Next.js (App Router), Tailwind CSS, Shadcn UI, TanStack Query.
- **Database**: SQLite (Development/Testing), PostgreSQL (Production).

## Getting Started

### Prerequisites

- **Node.js**: v20+ and `npm`
- **Python**: v3.12+
- **uv**: Recommended for Python dependency management (`pip install uv`)

### 1. Environment Setup

Copy the example environment files and adjust if necessary:

```bash
# Backend
cp apps/api/.env.example apps/api/.env

# Frontend
cp apps/web/.env.example apps/web/.env.local
```

### 2. Installation

Install dependencies for the entire project:

```bash
# Install root dev dependencies (concurrently)
npm install

# Install web dependencies
cd apps/web && npm install && cd ../..

# API dependencies are handled by uv automatically during scripts,
# but you can sync them manually:
cd apps/api && uv sync && cd ../..
```

### 3. Running the App

Run both API and Web in development mode:

```bash
npm run dev
```

- **API**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
- **Web**: [http://localhost:3000](http://localhost:3000)

### 4. Database & Seeding

The project includes a seed script to generate 10,000 realistic employee records for testing performance and analytics.

```bash
# Run the seed script
npm run seed
```

## Development Workflow

### Testing

We follow a TDD-first approach. Run all tests:

```bash
npm test
```

Or run them individually:
- `npm run test:api`
- `npm run test:web`

### Linting & Formatting

```bash
npm run lint    # Check for linting errors
npm run format  # Auto-format code
```

## Documentation

See the `docs/` folder for:
- `DESIGN_NOTES.md`: Data model, API contract, and validation rules.
- `TASK_BACKLOG.md`: Current progress and upcoming stories.
