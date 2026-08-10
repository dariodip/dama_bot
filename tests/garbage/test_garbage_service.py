from datetime import date
import pytest

import dama_bot.services.garbage as garbage
from dama_bot.services.garbage import GarbageService

@pytest.fixture
def service():
    return GarbageService()

def test_get_garbage_type_for_day(service):
    day = date(2026, 8, 10)
    assert service.get_garbage_type_for_day(day) == garbage.MULTIMATERIALE

    day = date(2026, 8, 11)
    assert service.get_garbage_type_for_day(day) == garbage.ORGANICO + " - " + garbage.CARTA_E_CARTONE

def test_get_garbage_type_for_day_niente(service):
    day = date(2026, 8, 8)
    assert service.get_garbage_type_for_day(day) == garbage.NIENTE

def test_get_garbage_type_wed(service):
    vetro_day = date(2026, 8, 12)
    assert garbage.VETRO in service.get_garbage_type_for_day(vetro_day)

    indiff_day = date(2026, 8, 19)
    assert garbage.INDIFFERENZIATA in service.get_garbage_type_for_day(indiff_day)

    vetro_day = date(2026, 10, 7)
    assert garbage.VETRO in service.get_garbage_type_for_day(vetro_day)

    indiff_day = date(2026, 10, 14)
    assert garbage.INDIFFERENZIATA in service.get_garbage_type_for_day(indiff_day)

def test_is_indifferenziato_week(service):
    vetro_day = date(2026, 8, 12)
    assert not service.is_indifferenziato_week(vetro_day)

    indiff_day = date(2026, 8, 19)
    assert service.is_indifferenziato_week(indiff_day)
