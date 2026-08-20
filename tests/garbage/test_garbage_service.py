from datetime import date

import pytest

from dama_bot.plugins.garbage.service import (
    CARTA_E_CARTONE,
    INDIFFERENZIATA,
    MULTIMATERIALE,
    NIENTE,
    ORGANICO,
    VETRO,
    GarbageService,
)


@pytest.fixture
def service():
    return GarbageService()


def test_get_garbage_type_for_day(service):
    day = date(2026, 8, 10)
    assert service.get_garbage_type_for_day(day) == MULTIMATERIALE

    day = date(2026, 8, 11)
    assert service.get_garbage_type_for_day(day) == (ORGANICO + " - " + CARTA_E_CARTONE)


def test_get_garbage_type_for_day_niente(service):
    day = date(2026, 8, 8)
    assert service.get_garbage_type_for_day(day) == NIENTE


def test_get_garbage_type_wed(service):
    vetro_day = date(2026, 8, 12)
    assert VETRO in service.get_garbage_type_for_day(vetro_day)

    indiff_day = date(2026, 8, 19)
    assert INDIFFERENZIATA in service.get_garbage_type_for_day(indiff_day)

    vetro_day = date(2026, 10, 7)
    assert VETRO in service.get_garbage_type_for_day(vetro_day)

    indiff_day = date(2026, 10, 14)
    assert INDIFFERENZIATA in service.get_garbage_type_for_day(indiff_day)


def test_is_indifferenziato_week(service):
    vetro_day = date(2026, 8, 12)
    assert not service.is_indifferenziato_week(vetro_day)

    indiff_day = date(2026, 8, 19)
    assert service.is_indifferenziato_week(indiff_day)
