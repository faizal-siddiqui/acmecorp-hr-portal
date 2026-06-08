import random
from datetime import date, timedelta

from faker import Faker

# Fixed seed for reproducibility
DEFAULT_SEED = 42

# Countries with their primary currency and a cost-of-living/market factor relative to USD
COUNTRIES = [
    {"code": "US", "currency": "USD", "cost_factor": 1.0},
    {"code": "GB", "currency": "GBP", "cost_factor": 0.85},
    {"code": "DE", "currency": "EUR", "cost_factor": 0.8},
    {"code": "FR", "currency": "EUR", "cost_factor": 0.75},
    {"code": "IN", "currency": "INR", "cost_factor": 0.3},
    {"code": "CA", "currency": "CAD", "cost_factor": 0.8},
    {"code": "AU", "currency": "AUD", "cost_factor": 0.85},
    {"code": "SG", "currency": "SGD", "cost_factor": 0.9},
    {"code": "BR", "currency": "BRL", "cost_factor": 0.4},
    {"code": "JP", "currency": "JPY", "cost_factor": 0.7},
]

DEPARTMENTS = [
    "Engineering",
    "Sales",
    "Marketing",
    "Finance",
    "HR",
    "Operations",
    "Support",
    "Product",
    "Legal",
    "Design",
]

LEVELS = ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]

# Base salary bands in USD (min, max) for each level
# These are "global" base bands that will be adjusted by country cost_factor
SALARY_BANDS: dict[str, tuple[int, int]] = {
    "L1": (40000, 60000),
    "L2": (60000, 90000),
    "L3": (90000, 130000),
    "L4": (130000, 180000),
    "L5": (180000, 250000),
    "L6": (250000, 350000),
    "L7": (350000, 500000),
}


def get_faker(seed: int = DEFAULT_SEED) -> Faker:
    """Returns a seeded Faker instance."""
    fake = Faker()
    fake.seed_instance(seed)
    return fake


class DataGenerator:
    def __init__(self, seed: int = DEFAULT_SEED):
        self.fake = get_faker(seed)

    def random_country(self) -> dict:
        return self.fake.random_element(COUNTRIES)

    def random_department(self) -> str:
        return self.fake.random_element(DEPARTMENTS)

    def random_level(self) -> str:
        # Weighted distribution: more junior/mid than principal
        # L1: 20%, L2: 25%, L3: 25%, L4: 15%, L5: 10%, L6: 4%, L7: 1%
        elements = LEVELS
        weights = [0.2, 0.25, 0.25, 0.15, 0.1, 0.04, 0.01]
        return random.choices(elements, weights=weights, k=1)[0]

    def get_salary_for_level(self, level: str, country_code: str) -> int:
        """
        Generates a realistic base salary for a given level and country.
        Adjusts the global USD band by the country's cost factor.
        """
        country = next(c for c in COUNTRIES if c["code"] == country_code)
        min_usd, max_usd = SALARY_BANDS[level]

        # Apply cost factor
        min_adj = int(min_usd * country["cost_factor"])
        max_adj = int(max_usd * country["cost_factor"])

        return self.fake.random_int(min=min_adj, max=max_adj)

    def get_bonus_for_level(self, level: str, base_salary: int) -> int:
        """
        Generates a realistic annual bonus.
        Higher levels typically have higher bonus percentages.
        """
        bonus_pct_map = {
            "L1": (0, 0.05),
            "L2": (0, 0.10),
            "L3": (0.05, 0.15),
            "L4": (0.10, 0.20),
            "L5": (0.15, 0.30),
            "L6": (0.20, 0.40),
            "L7": (0.30, 0.60),
        }
        min_pct, max_pct = bonus_pct_map[level]
        bonus_pct = self.fake.pyfloat(min_value=min_pct, max_value=max_pct)
        return int(base_salary * bonus_pct)

    def random_hire_date(self) -> date:
        """Generates a hire date within the last 10 years."""
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * 10)
        return self.fake.date_between(start_date=start_date, end_date=end_date)

    def random_status(self) -> str:
        """Generates a status: 95% active, 5% inactive."""
        return random.choices(["active", "inactive"], weights=[0.95, 0.05], k=1)[0]

    def generate_employee_basic(self, level: str, country: dict) -> dict:
        """Generates basic employee info (name, email, code)."""
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()
        # Use unique email to avoid collisions in large seeds
        email = self.fake.unique.email()
        employee_code = f"EMP-{self.fake.unique.random_number(digits=6, fix_len=True)}"

        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "employee_code": employee_code,
            "level": level,
            "country": country["code"],
            "status": self.random_status(),
        }
