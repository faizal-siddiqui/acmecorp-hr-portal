#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting setup for Salary Management System..."

# 1. Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# 2. Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
cd apps/web && npm install && cd ../..

# 3. Install backend dependencies
echo "🐍 Installing backend dependencies (using uv)..."
if ! command -v uv &> /dev/null
then
    echo "❌ 'uv' could not be found. Please install it first: https://github.com/astral-sh/uv"
    exit 1
fi
cd apps/api && uv sync --extra dev && cd ../..

# 4. Setup environment files
echo "⚙️ Setting up environment files..."
if [ ! -f apps/api/.env ]; then
    cp apps/api/.env.example apps/api/.env
    echo "  ✅ Created apps/api/.env"
else
    echo "  ℹ️ apps/api/.env already exists, skipping."
fi

if [ ! -f apps/web/.env.local ]; then
    cp apps/web/.env.example apps/web/.env.local
    echo "  ✅ Created apps/web/.env.local"
else
    echo "  ℹ️ apps/web/.env.local already exists, skipping."
fi

# 5. Seed the database
echo "🌱 Seeding the database (10,000 records)..."
npm run seed

# 6. Run the app
echo "✨ Setup complete! Starting development servers..."
npm run dev
