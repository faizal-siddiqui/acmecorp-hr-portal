from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories import AnalyticsRepository


@pytest.mark.asyncio
async def test_get_summary_data_logic():
    # Setup
    mock_db = MagicMock()

    # Mock result for salaries
    mock_result = MagicMock()
    mock_result.all.return_value = [(110000.0,), (93500.0,), (140000.0,)]
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Mock result for fx_as_of
    mock_fx_result = MagicMock()
    mock_fx_result.scalar.return_value = date(2026, 6, 6)

    # We need to handle multiple calls to execute
    async def side_effect(stmt):
        # Very simple way to distinguish the two queries in this test
        if "max" in str(stmt):
            return mock_fx_result
        return mock_result

    mock_db.execute.side_effect = side_effect

    repo = AnalyticsRepository(mock_db)

    # Execute
    data = await repo.get_summary_data()

    # Verify logic
    # Salaries: [110000, 93500, 140000]
    # Total: 343500
    # Avg: 114500
    # Median: 110000
    assert data["headcount"] == 3
    assert data["total_payroll_usd"] == 343500.0
    assert data["avg_payroll_usd"] == 114500.0
    assert data["median_payroll_usd"] == 110000.0
    assert data["fx_as_of"] == date(2026, 6, 6)


@pytest.mark.asyncio
async def test_get_breakdown_data_logic():
    # Setup
    mock_db = MagicMock()

    # Mock result for breakdown
    mock_result = MagicMock()
    # dimension_value, total_usd
    mock_result.all.return_value = [
        MagicMock(dimension_value="Engineering", total_usd=100000.0),
        MagicMock(dimension_value="Engineering", total_usd=120000.0),
        MagicMock(dimension_value="HR", total_usd=80000.0),
    ]
    mock_db.execute = AsyncMock(return_value=mock_result)

    repo = AnalyticsRepository(mock_db)

    # Execute
    data = await repo.get_breakdown_data(group_by="department")

    # Verify
    assert len(data) == 2

    eng = next(item for item in data if item["dimension_value"] == "Engineering")
    assert eng["count"] == 2
    assert eng["avg_usd"] == 110000.0
    assert eng["median_usd"] == 110000.0
    assert eng["min_usd"] == 100000.0
    assert eng["max_usd"] == 120000.0

    hr = next(item for item in data if item["dimension_value"] == "HR")
    assert hr["count"] == 1
    assert hr["avg_usd"] == 80000.0
    assert hr["median_usd"] == 80000.0
