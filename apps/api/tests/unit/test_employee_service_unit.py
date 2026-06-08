from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models import Compensation, FxRate
from app.schemas import CompensationUpdate
from app.services import EmployeeService


@pytest.mark.asyncio
async def test_update_compensation_unit():
    # Setup
    mock_repo = MagicMock()
    mock_repo.db = MagicMock()
    mock_repo.db.begin_nested = MagicMock()
    mock_repo.db.begin_nested.return_value.__aenter__ = AsyncMock()
    mock_repo.db.begin_nested.return_value.__aexit__ = AsyncMock()
    mock_repo.db.commit = AsyncMock()

    # Mock repository methods
    mock_repo.get_fx_rate = AsyncMock(return_value=FxRate(currency="USD", rate_to_usd=1.0))

    current_comp = Compensation(
        id=1,
        employee_id=1,
        base_annual=100000,
        bonus_annual=10000,
        currency="USD",
        effective_date=date(2020, 1, 1),
        is_current=True,
    )
    mock_repo.get_current_compensation = AsyncMock(return_value=current_comp)
    mock_repo.deactivate_compensations = AsyncMock()
    mock_repo.add_compensation = AsyncMock()
    mock_repo.add_history_records = AsyncMock()

    # Initialize service with mocked repository
    service = EmployeeService(None)
    service.repository = mock_repo

    update_data = CompensationUpdate(
        base_annual=120000, bonus_annual=15000, currency="USD", effective_date=date(2026, 1, 1)
    )

    # Execute
    result = await service.update_compensation(1, update_data, 99)

    # Verify
    assert result.base_annual == 120000
    assert result.bonus_annual == 15000

    # Verify repository calls
    mock_repo.get_fx_rate.assert_called_once_with("USD")
    mock_repo.get_current_compensation.assert_called_once_with(1)
    mock_repo.deactivate_compensations.assert_called_once_with(1)
    mock_repo.add_compensation.assert_called_once()

    # Verify history records
    mock_repo.add_history_records.assert_called_once()
    history_records = mock_repo.add_history_records.call_args[0][0]
    assert len(history_records) == 2
    fields = {h.field for h in history_records}
    assert "base_annual" in fields
    assert "bonus_annual" in fields


@pytest.mark.asyncio
async def test_update_compensation_invalid_currency_unit():
    # Setup
    mock_repo = MagicMock()
    mock_repo.get_fx_rate = AsyncMock(return_value=None)

    service = EmployeeService(None)
    service.repository = mock_repo

    update_data = CompensationUpdate(
        base_annual=120000, bonus_annual=15000, currency="XXX", effective_date=date(2026, 1, 1)
    )

    # Execute & Verify
    with pytest.raises(ValueError) as excinfo:
        await service.update_compensation(1, update_data, 99)
    assert "Currency XXX not found" in str(excinfo.value)
