# scenarios.py
from core.army import Army
from core.unit import Unit
from ai.generals_impl_IA import MajorDAFT

def lanchester_scenario(unit_class: type[Unit], n: int, general_class=MajorDAFT):
    """
    Creates a scenario for testing Lanchester's Laws.
    """
    army1_units = []
    for i in range(n):
        unit = unit_class(unit_id=i, army_id=0, pos=(10 + i * 2, 10))
        army1_units.append(unit)

    army2_units = []
    for i in range(2 * n):
        unit = unit_class(unit_id=1000 + i, army_id=1, pos=(10 + i * 2, 30))
        army2_units.append(unit)

    army1 = Army(army_id=0, units=army1_units, general=general_class(army_id=0))
    army2 = Army(army_id=1, units=army2_units, general=general_class(army_id=1))

    return army1, army2
