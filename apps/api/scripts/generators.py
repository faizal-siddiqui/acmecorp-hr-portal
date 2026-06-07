from faker import Faker
from typing import Dict, List, Tuple

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
SALARY_BANDS: Dict[str, Tuple[int, int]] = {
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

    def random_country(self) -> Dict:
        return self.fake.random_element(COUNTRIES)

    def random_department(self) -> str:
        return self.fake.random_element(DEPARTMENTS)

    def random_level(self) -> str:
        # Weighted distribution: more junior/mid than principal
        weights = [0.2, 0.25, 0.25, 0.15, 0.1, 0.04, 0.01]
        return self.fake.random_element(elements=LEVELS) # Faker doesn't support weights in random_element directly easily without choices

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
