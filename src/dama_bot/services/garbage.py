import logging
from datetime import date

logger = logging.getLogger(__name__)

MULTIMATERIALE = "Multimateriale"
ORGANICO = "Organico"
PANNOLINI = "Pannolini"
CARTA_E_CARTONE = "Carta & Cartone"
INDIFFERENZIATA = "Indifferenziata"
VETRO = "Vetro"
NIENTE = "Niente"

GARBAGE_SCHEDULE = {
    0: MULTIMATERIALE,
    1: ORGANICO + " - " + CARTA_E_CARTONE,
    2: [INDIFFERENZIATA, VETRO + " - " + PANNOLINI],
    3: MULTIMATERIALE,
    4: ORGANICO,
    5: NIENTE,
    6: ORGANICO + " - " + PANNOLINI,
}

class GarbageService():
    def __init__(self):
        pass

    def get_garbage_type_for_day(self, day: date):
        idx = day.weekday() % 7
        gs = GARBAGE_SCHEDULE[idx]
        if idx == 2:
            return gs[day.isocalendar().week % 2]
        return gs

    def is_indifferenziato_week(self, day: date):
        return day.isocalendar().week % 2 == 0
