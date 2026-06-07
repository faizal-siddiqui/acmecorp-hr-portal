"""
Seed script — Story A3.

Placeholder: full implementation (10 000 employees + fx_rates + HR user)
is done in Story A3 once the DB schema and ORM models exist (Story A2).

Usage:
    uv run python -m scripts.seed          # from apps/api/
    npm run seed                           # from repo root
"""


from scripts.generators import DataGenerator, COUNTRIES, DEPARTMENTS, LEVELS


def main() -> None:
    print("Seed script starting...")
    gen = DataGenerator(seed=42)
    
    # Placeholder for Story A3.2 and A3.3
    print(f"Loaded {len(COUNTRIES)} countries and {len(DEPARTMENTS)} departments.")
    print(f"Ready to generate 10,000 employees across {len(LEVELS)} levels.")
    
    print("Seed script not yet fully implemented -- coming in Story A3.2/A3.3.")


if __name__ == "__main__":
    main()
