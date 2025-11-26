# core/definitions.py
from ai.generals_impl_IA import CaptainBRAINDEAD, MajorDAFT, ColonelKAISER
from core.unit import (
    Knight, Pikeman, Crossbowman, LongSwordsman,
    EliteSkirmisher, CavalryArcher, Onager, Castle, Wonder
)

GENERAL_CLASS_MAP = {
    "CaptainBRAINDEAD": CaptainBRAINDEAD,
    "MajorDAFT": MajorDAFT,
    "ColonelKAISER": ColonelKAISER,
}

UNIT_CLASS_MAP = {
    "Knight": Knight,
    "Pikeman": Pikeman,
    "Crossbowman": Crossbowman,
    "LongSwordsman": LongSwordsman,
    "EliteSkirmisher": EliteSkirmisher,
    "CavalryArcher": CavalryArcher,
    "Onager": Onager,
    "Castle": Castle,
    "Wonder": Wonder,
}
