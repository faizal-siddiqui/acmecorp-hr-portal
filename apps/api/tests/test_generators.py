from scripts.generators import COUNTRIES, DEPARTMENTS, LEVELS, DataGenerator


def test_reproducibility():
    gen1 = DataGenerator(seed=42)
    gen2 = DataGenerator(seed=42)

    assert gen1.random_department() == gen2.random_department()
    assert gen1.random_country() == gen2.random_country()
    assert gen1.get_salary_for_level("L1", "US") == gen2.get_salary_for_level("L1", "US")


def test_random_country():
    gen = DataGenerator(seed=42)
    country = gen.random_country()
    assert country in COUNTRIES
    assert "code" in country
    assert "currency" in country
    assert "cost_factor" in country


def test_random_department():
    gen = DataGenerator(seed=42)
    dept = gen.random_department()
    assert dept in DEPARTMENTS


def test_salary_generation():
    gen = DataGenerator(seed=42)
    # US factor is 1.0, so salary should be within the base band
    salary_us = gen.get_salary_for_level("L1", "US")
    assert 40000 <= salary_us <= 60000

    # IN factor is 0.3, so salary should be around 30% of the base band
    salary_in = gen.get_salary_for_level("L1", "IN")
    assert int(40000 * 0.3) <= salary_in <= int(60000 * 0.3)


def test_random_level():
    gen = DataGenerator(seed=42)
    level = gen.random_level()
    assert level in LEVELS
