import pytest
from pydantic import ValidationError
from datetime import date
from app.schemas import CompensationUpdate

def test_compensation_update_valid():
    data = {
        "base_annual": 100000,
        "bonus_annual": 10000,
        "currency": "USD",
        "effective_date": "2026-01-01"
    }
    update = CompensationUpdate(**data)
    assert update.base_annual == 100000
    assert update.bonus_annual == 10000
    assert update.currency == "USD"
    assert update.effective_date == date(2026, 1, 1)

def test_compensation_update_invalid_base():
    with pytest.raises(ValidationError) as excinfo:
        CompensationUpdate(
            base_annual=0,
            bonus_annual=10000,
            currency="USD",
            effective_date="2026-01-01"
        )
    assert "Input should be greater than 0" in str(excinfo.value)

def test_compensation_update_invalid_bonus():
    with pytest.raises(ValidationError) as excinfo:
        CompensationUpdate(
            base_annual=100000,
            bonus_annual=-1,
            currency="USD",
            effective_date="2026-01-01"
        )
    assert "Input should be greater than or equal to 0" in str(excinfo.value)

def test_compensation_update_invalid_currency():
    with pytest.raises(ValidationError) as excinfo:
        CompensationUpdate(
            base_annual=100000,
            bonus_annual=10000,
            currency="US",
            effective_date="2026-01-01"
        )
    assert "String should have at least 3 characters" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        CompensationUpdate(
            base_annual=100000,
            bonus_annual=10000,
            currency="USDD",
            effective_date="2026-01-01"
        )
    assert "String should have at most 3 characters" in str(excinfo.value)
